from typing import Dict, Any

class PreprocessingService:
    

    def _get_median_weight(self, age: int) -> float:
        standards = {0: 3.3, 6: 7.5, 12: 9.6, 24: 12.2, 36: 14.3, 60: 18.3}
        return standards[min(standards, key=lambda x: abs(x - age))]

    def _get_median_height(self, age: int) -> float:
        standards = {0: 49.5, 6: 67.0, 12: 76.0, 24: 87.0, 36: 96.0, 60: 110.0}
        return standards[min(standards, key=lambda x: abs(x - age))]

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:

        cleaned = data.copy()

        age = cleaned.get("age_months")
        if age is None:
            age = 24  
            cleaned["age_months"] = age

        if cleaned.get("weight_kg") is None:
            cleaned["weight_kg"] = self._get_median_weight(age)

        if cleaned.get("height_cm") is None:
            cleaned["height_cm"] = self._get_median_height(age)

        for field in ["has_diarrhea", "has_malaria", "has_tb"]:
            if cleaned.get(field) is None:
                cleaned[field] = False

        if cleaned.get("gender"):
            cleaned["gender"] = str(cleaned["gender"]).capitalize()
        else:
            cleaned["gender"] = "Male" 

        if cleaned.get("mother_education"):
            edu = str(cleaned["mother_education"]).lower()
            if "no" in edu:
                cleaned["mother_education"] = "No education"
            elif "pri" in edu:
                cleaned["mother_education"] = "Primary"
            elif "sec" in edu:
                cleaned["mother_education"] = "Secondary"
            elif "high" in edu:
                cleaned["mother_education"] = "Higher"
            else:
                cleaned["mother_education"] = "Primary"  
        else:
            cleaned["mother_education"] = "Primary"

        if cleaned.get("household_wealth_index"):
            cleaned["household_wealth_index"] = str(cleaned["household_wealth_index"]).capitalize()
        else:
            cleaned["household_wealth_index"] = "Low" 

        cleaned["age_months"] = max(0, min(cleaned["age_months"], 60))

        cleaned["weight_kg"] = max(1.0, min(cleaned["weight_kg"], 40.0))

        cleaned["height_cm"] = max(30.0, min(cleaned["height_cm"], 150.0))

        return cleaned

preprocessing_service = PreprocessingService()
