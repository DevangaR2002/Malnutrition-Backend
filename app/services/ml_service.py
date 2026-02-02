import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from app.config import get_settings
import shap

settings = get_settings()


class HybridBoostingEnsemble:
    """Custom hybrid ensemble combining multiple boosting algorithms"""

    def __init__(self, models: dict = None, weights: dict = None):
        self.models = models or {}
        self.weights = weights or {
            'xgb_model': 0.35,
            'lgbm_model': 0.35,
            'catboost_model': 0.30
        }

    def predict_proba(self, X):
        probas = np.zeros((X.shape[0], 2))
        for name, model in self.models.items():
            if model is not None:
                probas += self.weights.get(name, 0.33) * model.predict_proba(X)
        return probas

    def predict(self, X):
        return (self.predict_proba(X)[:, 1] >= 0.5).astype(int)


class MLService:
    """Service for loading and using the ML model"""

    _instance = None
    _model = None
    _scaler = None
    _shap_explainer = None


    FEATURE_COLUMNS = [
        'Age (months)',
        'Gender_Encoded',
        'Age_Group_Encoded',
        'Mother_Education_Encoded',
        'Wealth_Index_Encoded',
        'Height_cm',
        'Weight_kg',
        'BMI',
        'Weight_Age_Ratio',
        'Height_Age_Ratio',
        'Disease_Count',
        'Region_Addis Ababa',
        'Region_Amhara',
        'Region_Oromia',
        'Region_SNNPR',
        'Region_Tigray'
    ]

    FEATURE_LABELS = {
    "Disease_Count": "active infections",
    "Mother_Education_Encoded": "maternal education level",
    "Wealth_Index_Encoded": "household economic status",
    "Age_Group_Encoded": "age-related vulnerability",
    "Weight_kg": "low body weight",
    "Height_cm": "linear growth",
    "Height_Age_Ratio": "height-for-age growth",
    "Weight_Age_Ratio": "weight-for-age growth",
    "BMI": "body mass index",
    "Gender_Encoded": "gender-related factors"
    }


    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_models()
        return cls._instance

    def _load_models(self):
        model_path = Path(settings.model_path)
        scaler_path = Path(settings.scaler_path)

        model_components = joblib.load(model_path)
        self._scaler = joblib.load(scaler_path)

        if isinstance(model_components, dict) and 'weights' in model_components:
            self._model = HybridBoostingEnsemble(
                models={
                    'xgb_model': model_components.get('xgb_model'),
                    'lgbm_model': model_components.get('lgbm_model'),
                    'catboost_model': model_components.get('catboost_model')
                },
                weights=model_components.get('weights')
            )
        else:
            self._model = model_components
    
        try:
            if isinstance(self._model, HybridBoostingEnsemble):
                base_model = self._model.models.get("xgb_model")
            else:
                base_model = self._model

            if base_model is not None:
                self._shap_explainer = shap.TreeExplainer       (base_model)
        except Exception as e:
            self._shap_explainer = None


    def _prepare_features(self, data: dict) -> pd.DataFrame:
        age = data['age_months']
        height_m = data['height_cm'] / 100
        bmi = data['weight_kg'] / (height_m ** 2) if height_m > 0 else 0

        weight_age_ratio = data['weight_kg'] / age if age > 0 else 0
        height_age_ratio = data['height_cm'] / age if age > 0 else 0

        bmi = min(max(bmi, 5), 40)
        weight_age_ratio = min(max(weight_age_ratio, 0), 5)
        height_age_ratio = min(max(height_age_ratio, 0), 30)

        disease_count = sum([
            data.get('has_diarrhea', False),
            data.get('has_malaria', False),
            data.get('has_tb', False)
        ])

        gender_encoded = 1 if data['gender'] == 'Male' else 0
        edu_map = {'No education': 0, 'Primary': 1, 'Secondary': 2, 'Higher': 3}
        wealth_map = {'Low': 0, 'Middle': 1, 'High': 2}

        age_group = (
            0 if age <= 6 else
            1 if age <= 12 else
            2 if age <= 24 else
            3 if age <= 36 else
            4 if age <= 60 else 5
        )

        return pd.DataFrame({
            'Age (months)': [age],
            'Gender_Encoded': [gender_encoded],
            'Age_Group_Encoded': [age_group],
            'Mother_Education_Encoded': [edu_map.get(data['mother_education'], 0)],
            'Wealth_Index_Encoded': [wealth_map.get(data['household_wealth_index'], 0)],
            'Height_cm': [data['height_cm']],
            'Weight_kg': [data['weight_kg']],
            'BMI': [bmi],
            'Weight_Age_Ratio': [weight_age_ratio],
            'Height_Age_Ratio': [height_age_ratio],
            'Disease_Count': [disease_count],
            'Region_Addis Ababa': [0.0],
            'Region_Amhara': [0.0],
            'Region_Oromia': [0.0],
            'Region_SNNPR': [1.0],
            'Region_Tigray': [0.0]
        })
    

    def _generate_xai(self, scaled_df: pd.DataFrame) -> dict | None:
        """
        Generate local XAI using SHAP.
        Returns top contributing factors only.
        """
        if self._shap_explainer is None:
            return None

        try:
            shap_values = self._shap_explainer.shap_values(scaled_df)

            if isinstance(shap_values, list):
                shap_values = shap_values[1]

            row = shap_values[0]
            features = scaled_df.columns

            impacts = sorted(
                zip(features, row),
                key=lambda x: abs(x[1]),
                reverse=True
            )

            return {
                "top_factors": [
                    {
                        "feature": f,
                        "impact": float(v)
                    }
                    for f, v in impacts[:5]
                ]
            }

        except Exception:
            return None
    
    def _xai_to_human_text(self, xai: dict | None) -> str:
        """
        Convert SHAP output into clinically safe, neutral explanation text.
        """

        if xai is None:
            return (
                "This assessment was determined using clinical rule-based criteria. "
                "The child shows no active infections, adequate growth indicators, "
                "and favorable socioeconomic conditions."
            )

        if "top_factors" not in xai or not xai["top_factors"]:
            return (
                "A machine learning assessment was performed, but no dominant "
                "factors influencing the prediction were identified."
            )

        factors = []

        for item in xai["top_factors"]:
            feature = item["feature"]
            label = self.FEATURE_LABELS.get(feature, feature)
            factors.append(label)

        return (
            "This prediction was influenced by multiple factors considered together, "
            "including " + ", ".join(factors) +
            ". These indicate how the model weighted the information and should not "
            "be interpreted as direct causes or protective effects."
        )




    def predict(self, data: dict) -> dict:

        if self._passes_clear_low_risk_rules(data):
            xai = None
            xai_text = self._xai_to_human_text(None)
            return {
                "prediction": 0,
                "risk_level": "Low Risk",
                "risk_probability": 0.05,
                "confidence": "High",
                "recommendations": self._generate_who_recommendations(
                    data, prediction=0, probability=0.05
                ),
                "xai": xai,
                "xai_text": xai_text
            }

        features = self._prepare_features(data)
        scaled = self._scaler.transform(features)
        scaled_df = pd.DataFrame(scaled, columns=self.FEATURE_COLUMNS)
        xai = self._generate_xai(scaled_df)
        xai_text = self._xai_to_human_text(xai)

        proba = self._model.predict_proba(scaled_df)[0]
        risk_probability = float(proba[1])

        if risk_probability >= 0.80:
            risk_level = "High Risk"
            prediction = 1
        else:
            risk_level = "Low Risk"
            prediction = 0

        if risk_probability >= 0.80:
            confidence = "High"
        elif risk_probability >=0.60:
            confidence = "Medium"
        else:
            confidence = "Low"


        recommendations = self._generate_who_recommendations(
            data,
            prediction=prediction,
            probability=risk_probability
        )

        return {
            "prediction": prediction,
            "risk_level": risk_level,
            "risk_probability": risk_probability,
            "confidence": confidence,
            "recommendations": recommendations,
            "xai": xai,
            "xai_text" : xai_text
        }

    def _generate_who_recommendations(self, data: dict, prediction: int, probability: float) -> list:
        
        recommendations = []
  
        height_m = data['height_cm'] / 100
        bmi = data['weight_kg'] / (height_m ** 2) if height_m > 0 else 0
        
        age = data['age_months']
        
        if prediction == 1:  # HIGH RISK - Malnourished/At Risk
            
            # Immediate action [2]
            recommendations.append({
                "category": "Immediate Action Required",
                "recommendation": "Assess severity using WHO Child Growth Standards; if severe, manage as Severe Acute Malnutrition (SAM) with RUTF, medical treatment, and referral; if moderate, provide supplementary feeding and close follow-up.",
                "source": "WHO SAM Guidelines (2013)"
            })
            
            # Low Weight (Wasting) [2]
            if bmi < 14 or data['weight_kg'] < self._get_expected_weight(age) * 0.8:
                recommendations.append({
                    "category": "Low Weight (Wasting)",
                    "recommendation": "Identify underlying causes (poor intake, infections); implement supplementary feeding; treat illnesses; monitor growth frequently.",
                    "source": "WHO Management of Moderate Acute Malnutrition; WHO Malnutrition Fact Sheet"
                })
            
            # Stunting [2]
            if data['height_cm'] < self._get_expected_height(age) * 0.9:
                recommendations.append({
                    "category": "Stunting (Chronic Undernutrition)",
                    "recommendation": "Promote optimal IYCF, maternal nutrition, disease prevention, and sanitation; long-term monitoring and early childhood interventions.",
                    "source": "WHO & UNICEF Global Strategy for IYCF"
                })
            
            # TB [2]
            if data.get('has_tb'):
                recommendations.append({
                    "category": "Tuberculosis (TB)",
                    "recommendation": "Diagnose and start prompt anti-TB treatment according to WHO pediatric TB treatment guidelines; ensure appropriate drug regimen, consider nutritional assessment and support during TB treatment; monitor closely for response and side effects.",
                    "source": "WHO Consolidated Guidelines on TB: Module 5"
                })
            
            # Malaria [2]
            if data.get('has_malaria'):
                recommendations.append({
                    "category": "Malaria",
                    "recommendation": "Prompt diagnosis and treatment according to malaria guidelines; integrate nutrition rehabilitation during recovery. Implement malaria prevention (bed nets, vector control).",
                    "source": "WHO Malaria Treatment Guidelines"
                })
            
            # Diarrhea [2]
            if data.get('has_diarrhea'):
                recommendations.append({
                    "category": "Diarrhea Management",
                    "recommendation": "Manage with ORS and zinc supplementation; continue feeding during illness; monitor weight to prevent acute malnutrition.",
                    "source": "WHO & UNICEF Diarrhoea Management Guidelines"
                })
            
            # Low household wealth [2]
            if data['household_wealth_index'] == 'Low':
                recommendations.append({
                    "category": "Low Household Wealth",
                    "recommendation": "Prioritize social protection, food assistance programmes, targeted supplementation, and community nutrition support.",
                    "source": "WHO Malnutrition Fact Sheet; WHO Essential Nutrition Actions"
                })
            
            # Low maternal education [2]
            if data['mother_education'] in ['No education', 'Primary']:
                recommendations.append({
                    "category": "Caregiver Education",
                    "recommendation": "Intensive caregiver education on feeding, hygiene, danger signs, and healthcare-seeking behaviours.",
                    "source": "WHO Essential Nutrition Actions (2013)"
                })
            
            # Age-specific feeding recommendations
            if age <= 6:
                recommendations.append({
                    "category": "Infant Feeding (0-6 months)",
                    "recommendation": "Ensure exclusive breastfeeding for the first 6 months. Assess breastfeeding practices and provide lactation support.",
                    "source": "WHO & UNICEF Global Strategy for IYCF"
                })
            elif age <= 24:
                recommendations.append({
                    "category": "Complementary Feeding (6-24 months)",
                    "recommendation": "Introduce diverse complementary foods alongside continued breastfeeding. Ensure adequate meal frequency.",
                    "source": "WHO Essential Nutrition Actions (2013)"
                })
            
            # Growth monitoring
            recommendations.append({
                "category": "Growth Monitoring",
                "recommendation": "Regular monitoring of growth parameters; schedule frequent follow-up visits to track weight, height, and MUAC.",
                "source": "WHO Child Growth Standards"
            })
        
        else:  # LOW RISK - Well-Nourished
            
            # Current status [2]
            recommendations.append({
                "category": "Current Status",
                "recommendation": "Child appears to be well-nourished. Continue current nutrition and health practices.",
                "source": "WHO Child Growth Standards"
            })
            
            # Nutrition maintenance [2]
            recommendations.append({
                "category": "Nutrition Maintenance",
                "recommendation": "Continue age-appropriate balanced diet; routine growth monitoring to detect early weight loss; caregiver counselling on adequate energy intake.",
                "source": "WHO SAM Guidelines (2013)"
            })
            
            # Periodic monitoring [2]
            recommendations.append({
                "category": "Growth Monitoring",
                "recommendation": "Maintain adequate nutrition and health practices; periodic growth monitoring to ensure linear growth continues normally.",
                "source": "WHO Essential Nutrition Actions (2013); WHO Malnutrition Fact Sheet (2024)"
            })
            
            # Disease management even if low risk [2]
            if data.get('has_tb'):
                recommendations.append({
                    "category": "TB Management",
                    "recommendation": "Standard pediatric TB management per WHO guidelines; ensure early diagnosis and treatment; emphasize preventive therapy for contacts.",
                    "source": "WHO Consolidated Guidelines on TB: Module 5"
                })
            
            if data.get('has_malaria'):
                recommendations.append({
                    "category": "Malaria Prevention",
                    "recommendation": "Malaria prevention (bed nets, vector control); routine nutrition and health monitoring.",
                    "source": "WHO Malaria Treatment Guidelines"
                })
            
            if data.get('has_diarrhea'):
                recommendations.append({
                    "category": "Diarrhea Management",
                    "recommendation": "Promote hygiene, safe water, and sanitation; continued feeding and fluid intake during mild illness.",
                    "source": "WHO & UNICEF Diarrhoea Management Guidelines"
                })
            
            # Low household wealth - preventive support [2]
            if data['household_wealth_index'] == 'Low':
                recommendations.append({
                    "category": "Preventive Support",
                    "recommendation": "Continue preventive nutrition services and growth monitoring; ensure food security is maintained.",
                    "source": "WHO Malnutrition Fact Sheet; WHO Essential Nutrition Actions"
                })
            
            # Low maternal education - ongoing education [2]
            if data['mother_education'] in ['No education', 'Primary']:
                recommendations.append({
                    "category": "Ongoing Education",
                    "recommendation": "Ongoing health education reinforcement; empower caregivers to sustain good practices.",
                    "source": "WHO Essential Nutrition Actions (2013)"
                })
            
            # Family practices [2]
            recommendations.append({
                "category": "Family Practices",
                "recommendation": "Sustain appropriate feeding practices, maternal health, and hygiene to prevent future growth faltering.",
                "source": "WHO & UNICEF Global Strategy for IYCF"
            })
            
            # Warning if probability is borderline
            if probability > 0.3:
                recommendations.append({
                    "category": "Monitoring Alert",
                    "recommendation": "Although classified as low risk, there are some risk indicators present. Monitor more closely and reassess if any health changes occur.",
                    "source": "Clinical Assessment"
                })
        
        return recommendations

    def _get_expected_weight(self, age):
        standards = {0:3.3,6:7.5,12:9.6,24:12.2,36:14.3,60:18.3}
        return standards[min(standards, key=lambda x: abs(x-age))]

    def _get_expected_height(self, age):
        standards = {0:49.5,6:67.0,12:76.0,24:87.0,36:96.0,60:110.0}
        return standards[min(standards, key=lambda x: abs(x-age))]

    def _passes_clear_low_risk_rules(self, data: dict) -> bool:
        age = data["age_months"]
        if data.get("has_diarrhea") or data.get("has_malaria") or data.get("has_tb"):
            return False
        if data["household_wealth_index"] == "Low":
            return False
        if data["mother_education"] in ["No education", "Primary"]:
            return False
        if data["weight_kg"] < self._get_expected_weight(age) * 0.9:
            return False
        if data["height_cm"] < self._get_expected_height(age) * 0.9:
            return False
        return True


ml_service = MLService()

