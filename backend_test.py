import requests
import sys
import json
from datetime import datetime

class AnimalVoiceLabAPITester:
    def __init__(self, base_url="https://animal-voice-lab.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def run_test(self, name, method, endpoint, expected_status, data=None, expected_fields=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)

            success = response.status_code == expected_status
            response_data = {}
            
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}

            if success:
                # Check for expected fields if provided
                if expected_fields and isinstance(response_data, dict):
                    for field in expected_fields:
                        if field not in response_data:
                            success = False
                            print(f"❌ Failed - Missing expected field: {field}")
                            break
                
                if success:
                    self.tests_passed += 1
                    print(f"✅ Passed - Status: {response.status_code}")
                    if isinstance(response_data, dict) and len(str(response_data)) < 500:
                        print(f"   Response: {json.dumps(response_data, indent=2)}")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")

            self.test_results.append({
                "test": name,
                "success": success,
                "status_code": response.status_code,
                "expected_status": expected_status,
                "response_size": len(response.text)
            })

            return success, response_data

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.test_results.append({
                "test": name,
                "success": False,
                "error": str(e)
            })
            return False, {}

    def test_root_endpoint(self):
        """Test API root endpoint"""
        return self.run_test(
            "API Root",
            "GET",
            "",
            200,
            expected_fields=["message"]
        )

    def test_get_animals(self):
        """Test getting list of animals"""
        success, response = self.run_test(
            "Get Animals List",
            "GET",
            "animals",
            200,
            expected_fields=["animals"]
        )
        
        if success and "animals" in response:
            animals = response["animals"]
            expected_animals = ["monkey", "dog", "cat", "horse", "lion", "parrot", "tiger"]
            
            print(f"   Found {len(animals)} animals")
            animal_ids = [animal["id"] for animal in animals]
            
            # Check if all expected animals are present
            missing_animals = [animal for animal in expected_animals if animal not in animal_ids]
            if missing_animals:
                print(f"   ⚠️  Missing animals: {missing_animals}")
            else:
                print(f"   ✅ All 7 expected animals found: {animal_ids}")
                
            return success, animals
        
        return success, []

    def test_get_animal_details(self, animal_id):
        """Test getting specific animal details"""
        success, response = self.run_test(
            f"Get Animal Details - {animal_id}",
            "GET",
            f"animals/{animal_id}",
            200,
            expected_fields=["name", "scientific_name", "vocalizations", "expressions"]
        )
        
        if success:
            print(f"   Animal: {response.get('name', 'Unknown')}")
            print(f"   Vocalizations: {len(response.get('vocalizations', []))}")
            print(f"   Expressions: {len(response.get('expressions', []))}")
            
        return success, response

    def test_get_vocalizations(self, animal_id):
        """Test getting animal vocalizations"""
        return self.run_test(
            f"Get Vocalizations - {animal_id}",
            "GET",
            f"animals/{animal_id}/vocalizations",
            200,
            expected_fields=["vocalizations"]
        )

    def test_get_expressions(self, animal_id):
        """Test getting animal expressions"""
        return self.run_test(
            f"Get Expressions - {animal_id}",
            "GET",
            f"animals/{animal_id}/expressions",
            200,
            expected_fields=["expressions"]
        )

    def test_analyze_vocalization(self, animal_id, vocalization_id):
        """Test analyzing a vocalization"""
        data = {
            "animal_id": animal_id,
            "vocalization_id": vocalization_id,
            "context": "Testing vocalization analysis"
        }
        
        success, response = self.run_test(
            f"Analyze Vocalization - {animal_id}/{vocalization_id}",
            "POST",
            "analyze",
            200,
            data=data,
            expected_fields=["id", "animal", "input_type", "human_translation", "context_meaning", "behavioral_insight"]
        )
        
        if success:
            print(f"   Translation: {response.get('human_translation', 'N/A')[:100]}...")
            
        return success, response

    def test_analyze_expression(self, animal_id, expression_id):
        """Test analyzing an expression"""
        data = {
            "animal_id": animal_id,
            "expression_id": expression_id,
            "context": "Testing expression analysis"
        }
        
        success, response = self.run_test(
            f"Analyze Expression - {animal_id}/{expression_id}",
            "POST",
            "analyze",
            200,
            data=data,
            expected_fields=["id", "animal", "input_type", "human_translation", "context_meaning", "behavioral_insight"]
        )
        
        if success:
            print(f"   Translation: {response.get('human_translation', 'N/A')[:100]}...")
            
        return success, response

    def test_get_analysis_history(self):
        """Test getting analysis history"""
        return self.run_test(
            "Get Analysis History",
            "GET",
            "analysis/history?limit=5",
            200,
            expected_fields=["history"]
        )

    def test_invalid_animal(self):
        """Test with invalid animal ID"""
        return self.run_test(
            "Invalid Animal ID",
            "GET",
            "animals/invalid_animal",
            404
        )

    def test_invalid_analysis(self):
        """Test analysis with invalid data"""
        data = {
            "animal_id": "invalid_animal",
            "vocalization_id": "invalid_vocalization"
        }
        
        return self.run_test(
            "Invalid Analysis Request",
            "POST",
            "analyze",
            404,
            data=data
        )

def main():
    print("🧪 Starting Animal Voice Lab API Tests")
    print("=" * 50)
    
    tester = AnimalVoiceLabAPITester()
    
    # Test basic endpoints
    tester.test_root_endpoint()
    
    # Test animals endpoint
    animals_success, animals = tester.test_get_animals()
    
    if animals_success and animals:
        # Test first animal in detail
        first_animal = animals[0]
        animal_id = first_animal["id"]
        
        # Test animal details
        animal_success, animal_data = tester.test_get_animal_details(animal_id)
        
        if animal_success:
            # Test vocalizations and expressions endpoints
            tester.test_get_vocalizations(animal_id)
            tester.test_get_expressions(animal_id)
            
            # Test analysis with first vocalization and expression
            if animal_data.get("vocalizations"):
                first_vocalization = animal_data["vocalizations"][0]["id"]
                tester.test_analyze_vocalization(animal_id, first_vocalization)
                
            if animal_data.get("expressions"):
                first_expression = animal_data["expressions"][0]["id"]
                tester.test_analyze_expression(animal_id, first_expression)
    
    # Test analysis history
    tester.test_get_analysis_history()
    
    # Test error cases
    tester.test_invalid_animal()
    tester.test_invalid_analysis()
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"Tests run: {tester.tests_run}")
    print(f"Tests passed: {tester.tests_passed}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"❌ {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())