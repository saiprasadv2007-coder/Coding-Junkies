from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Animal Data - Predefined expressions and vocalizations
# Audio URLs from BigSoundBank (free, royalty-free)
ANIMALS_DATA = {
    "monkey": {
        "name": "Monkey",
        "scientific_name": "Primates",
        "image": "https://images.unsplash.com/photo-1668335529036-7de688096d3b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA1NTJ8MHwxfHNlYXJjaHwyfHxtb25rZXklMjBmYWNlJTIwcG9ydHJhaXR8ZW58MHx8fHwxNzc1NDYwMzQwfDA&ixlib=rb-4.1.0&q=85",
        "vocalizations": [
            {"id": "monkey_screech", "name": "Screech", "context": "alarm", "audio_url": "https://bigsoundbank.com/UPLOAD/mp3/0170.mp3", "description": "High-pitched alarm call warning of predators"},
            {"id": "monkey_chatter", "name": "Chatter", "context": "social", "audio_url": "https://bigsoundbank.com/UPLOAD/mp3/1070.mp3", "description": "Social communication between group members"},
            {"id": "monkey_hoot", "name": "Hoot", "context": "territorial", "audio_url": "https://bigsoundbank.com/UPLOAD/mp3/0653.mp3", "description": "Territorial call to establish dominance"}
        ],
        "expressions": [
            {"id": "monkey_teeth_bared", "name": "Teeth Bared", "emotion": "fear/submission", "meaning": "I feel threatened and am showing submission"},
            {"id": "monkey_lip_smack", "name": "Lip Smacking", "emotion": "friendly", "meaning": "I want to be friends and show I'm not a threat"},
            {"id": "monkey_stare", "name": "Direct Stare", "emotion": "aggressive", "meaning": "I am challenging you - back off!"},
            {"id": "monkey_relaxed", "name": "Relaxed Face", "emotion": "content", "meaning": "I feel safe and comfortable"}
        ]
    },
    "dog": {
        "name": "Dog",
        "scientific_name": "Canis lupus familiaris",
        "image": "https://static.prod-images.emergentagent.com/jobs/e8cf87b4-f34d-45c3-905e-15665110f855/images/d45c850154606f68e31aee15e96c04227008e560a862b25eb0aec1aca8fcfb4e.png",
        "vocalizations": [
            {"id": "dog_bark", "name": "Bark", "context": "alert", "audio_url": "https://bigsoundbank.com/UPLOAD/mp3/0288.mp3", "description": "Alert bark to notify of presence or danger"},
            {"id": "dog_whine", "name": "Whine", "context": "need", "audio_url": "https://bigsoundbank.com/UPLOAD/mp3/1544.mp3", "description": "Expression of need, discomfort, or anxiety"},
            {"id": "dog_growl", "name": "Growl", "context": "warning", "audio_url": "https://bigsoundbank.com/UPLOAD/mp3/0682.mp3", "description": "Warning signal indicating displeasure or threat"},
            {"id": "dog_howl", "name": "Howl", "context": "communication", "audio_url": "https://bigsoundbank.com/UPLOAD/mp3/2450.mp3", "description": "Long-distance communication or response to sounds"}
        ],
        "expressions": [
            {"id": "dog_happy", "name": "Happy/Excited", "emotion": "joy", "meaning": "I'm so happy to see you! Let's play!"},
            {"id": "dog_submissive", "name": "Ears Back", "emotion": "submissive", "meaning": "I recognize your authority and mean no harm"},
            {"id": "dog_alert", "name": "Ears Forward", "emotion": "alert", "meaning": "Something has my attention - I'm investigating"},
            {"id": "dog_anxious", "name": "Whale Eye", "emotion": "anxious", "meaning": "I'm uncomfortable with this situation"}
        ]
    },
    "cat": {
        "name": "Cat",
        "scientific_name": "Felis catus",
        "image": "https://static.prod-images.emergentagent.com/jobs/e8cf87b4-f34d-45c3-905e-15665110f855/images/33a08cb367948e44e5dc0d6d772049010bf980f684400451f9febaa0e20f31f7.png",
        "vocalizations": [
            {"id": "cat_meow", "name": "Meow", "context": "communication", "audio_url": "https://bigsoundbank.com/UPLOAD/mp3/1890.mp3", "description": "Primary vocalization for human communication"},
            {"id": "cat_purr", "name": "Purr", "context": "contentment", "audio_url": "https://bigsoundbank.com/UPLOAD/mp3/0436.mp3", "description": "Sign of contentment or self-soothing"},
            {"id": "cat_hiss", "name": "Hiss", "context": "defensive", "audio_url": "https://bigsoundbank.com/UPLOAD/mp3/1887.mp3", "description": "Defensive warning to back away"},
            {"id": "cat_chirp", "name": "Chirp/Trill", "context": "greeting", "audio_url": "https://bigsoundbank.com/UPLOAD/mp3/0098.mp3", "description": "Friendly greeting or attention-seeking"}
        ],
        "expressions": [
            {"id": "cat_slow_blink", "name": "Slow Blink", "emotion": "affection", "meaning": "I trust you completely - you're my friend"},
            {"id": "cat_dilated", "name": "Dilated Pupils", "emotion": "excited/fearful", "meaning": "I'm highly stimulated - excited or scared"},
            {"id": "cat_flattened_ears", "name": "Flattened Ears", "emotion": "aggressive", "meaning": "I'm ready to fight - don't push me"},
            {"id": "cat_relaxed", "name": "Half-Closed Eyes", "emotion": "relaxed", "meaning": "I feel completely safe and content"}
        ]
    },
    "horse": {
        "name": "Horse",
        "scientific_name": "Equus caballus",
        "image": "https://static.prod-images.emergentagent.com/jobs/e8cf87b4-f34d-45c3-905e-15665110f855/images/b645448038b61c3021155472e544c3a6f4b610cfceb3301268fa90bbe0698d78.png",
        "vocalizations": [
            {"id": "horse_neigh", "name": "Neigh/Whinny", "context": "social", "audio_url": "https://bigsoundbank.com/UPLOAD/mp3/0863.mp3", "description": "Social call to locate or greet other horses"},
            {"id": "horse_snort", "name": "Snort", "context": "alert", "audio_url": "https://bigsoundbank.com/UPLOAD/mp3/0611.mp3", "description": "Alert signal or clearing of airways"},
            {"id": "horse_nicker", "name": "Nicker", "context": "affection", "audio_url": "https://bigsoundbank.com/UPLOAD/mp3/1543.mp3", "description": "Soft greeting showing affection"},
            {"id": "horse_squeal", "name": "Squeal", "context": "excitement", "audio_url": "https://bigsoundbank.com/UPLOAD/mp3/0289.mp3", "description": "Excitement or displeasure during interaction"}
        ],
        "expressions": [
            {"id": "horse_ears_forward", "name": "Ears Forward", "emotion": "alert/interested", "meaning": "Something caught my attention - I'm curious"},
            {"id": "horse_ears_back", "name": "Ears Pinned Back", "emotion": "angry", "meaning": "I'm warning you - I may bite or kick"},
            {"id": "horse_relaxed_lip", "name": "Droopy Lower Lip", "emotion": "relaxed", "meaning": "I'm completely relaxed and content"},
            {"id": "horse_flehmen", "name": "Flehmen Response", "emotion": "curious", "meaning": "I'm analyzing an interesting scent"}
        ]
    },
    "lion": {
        "name": "Lion",
        "scientific_name": "Panthera leo",
        "image": "https://static.prod-images.emergentagent.com/jobs/e8cf87b4-f34d-45c3-905e-15665110f855/images/1871709622b750c472dc9976cdf99a180b683d109456c984ab7b04cd2ee04048.png",
        "vocalizations": [
            {"id": "lion_roar", "name": "Roar", "context": "territorial", "audio_url": "https://bigsoundbank.com/UPLOAD/mp3/1810.mp3", "description": "Territorial call heard up to 5 miles away"},
            {"id": "lion_growl", "name": "Growl", "context": "warning", "audio_url": "https://bigsoundbank.com/UPLOAD/mp3/2107.mp3", "description": "Warning signal during confrontation"},
            {"id": "lion_grunt", "name": "Grunt", "context": "contact", "audio_url": "https://bigsoundbank.com/UPLOAD/mp3/0486.mp3", "description": "Soft contact call within the pride"},
            {"id": "lion_snarl", "name": "Snarl", "context": "aggressive", "audio_url": "https://bigsoundbank.com/UPLOAD/mp3/2108.mp3", "description": "Aggressive display during conflict"}
        ],
        "expressions": [
            {"id": "lion_yawn", "name": "Wide Yawn", "emotion": "relaxed/display", "meaning": "I'm relaxed, or showing my powerful teeth"},
            {"id": "lion_stare", "name": "Fixed Stare", "emotion": "focused", "meaning": "I'm locked onto my target - hunting or warning"},
            {"id": "lion_head_rub", "name": "Head Rubbing", "emotion": "social bonding", "meaning": "You're part of my pride - I'm marking you"},
            {"id": "lion_ears_flat", "name": "Ears Flattened", "emotion": "aggressive", "meaning": "I'm about to attack - final warning"}
        ]
    },
    "parrot": {
        "name": "Parrot",
        "scientific_name": "Psittaciformes",
        "image": "https://images.unsplash.com/photo-1660292294670-67aa87d93055?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjY2NzF8MHwxfHNlYXJjaHwyfHxtYWNhdyUyMHBhcnJvdCUyMGZhY2UlMjBwb3J0cmFpdHxlbnwwfHx8fDE3NzU0NjAzMzl8MA&ixlib=rb-4.1.0&q=85",
        "vocalizations": [
            {"id": "parrot_squawk", "name": "Squawk", "context": "alert", "audio_url": "https://bigsoundbank.com/UPLOAD/mp3/2776.mp3", "description": "Loud alarm call for danger or attention"},
            {"id": "parrot_chatter", "name": "Chatter", "context": "happy", "audio_url": "https://bigsoundbank.com/UPLOAD/mp3/2781.mp3", "description": "Content sounds when comfortable"},
            {"id": "parrot_whistle", "name": "Whistle", "context": "social", "audio_url": "https://bigsoundbank.com/UPLOAD/mp3/1165.mp3", "description": "Social call to connect with flock"},
            {"id": "parrot_screech", "name": "Screech", "context": "distress", "audio_url": "https://bigsoundbank.com/UPLOAD/mp3/2779.mp3", "description": "High-pitched distress or excitement call"}
        ],
        "expressions": [
            {"id": "parrot_pinning", "name": "Eye Pinning", "emotion": "excited/focused", "meaning": "I'm very interested or excited about something"},
            {"id": "parrot_fluffed", "name": "Fluffed Feathers", "emotion": "relaxed/cold", "meaning": "I'm comfortable and relaxing, or feeling chilly"},
            {"id": "parrot_crest_up", "name": "Raised Crest", "emotion": "alert/excited", "meaning": "Something has my attention - I'm stimulated"},
            {"id": "parrot_beak_grind", "name": "Beak Grinding", "emotion": "content", "meaning": "I'm happy and settling down to rest"}
        ]
    },
    "tiger": {
        "name": "Tiger",
        "scientific_name": "Panthera tigris",
        "image": "https://images.unsplash.com/photo-1661769212734-67877c79deff?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzh8MHwxfHNlYXJjaHwxfHx0aWdlciUyMGZhY2UlMjBwb3J0cmFpdHxlbnwwfHx8fDE3NzU0NjAzMzl8MA&ixlib=rb-4.1.0&q=85",
        "vocalizations": [
            {"id": "tiger_roar", "name": "Roar", "context": "territorial", "audio_url": "https://bigsoundbank.com/UPLOAD/mp3/0929.mp3", "description": "Powerful territorial announcement"},
            {"id": "tiger_chuff", "name": "Chuff/Prusten", "context": "friendly", "audio_url": "https://bigsoundbank.com/UPLOAD/mp3/1809.mp3", "description": "Friendly greeting sound - unique to tigers"},
            {"id": "tiger_growl", "name": "Growl", "context": "warning", "audio_url": "https://bigsoundbank.com/UPLOAD/mp3/2110.mp3", "description": "Warning signal during confrontation"},
            {"id": "tiger_moan", "name": "Moan", "context": "communication", "audio_url": "https://bigsoundbank.com/UPLOAD/mp3/0170.mp3", "description": "Long-distance communication call"}
        ],
        "expressions": [
            {"id": "tiger_relaxed", "name": "Relaxed Face", "emotion": "calm", "meaning": "I'm at peace and not threatened"},
            {"id": "tiger_snarl", "name": "Snarl/Teeth Bared", "emotion": "aggressive", "meaning": "This is your final warning - I will attack"},
            {"id": "tiger_squint", "name": "Squinted Eyes", "emotion": "content", "meaning": "I feel safe and comfortable with you"},
            {"id": "tiger_ears_back", "name": "Ears Rotated Back", "emotion": "defensive", "meaning": "I'm feeling threatened and ready to defend"}
        ]
    }
}

# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

class AnalysisRequest(BaseModel):
    animal_id: str
    vocalization_id: Optional[str] = None
    expression_id: Optional[str] = None
    context: Optional[str] = None

class AnalysisResponse(BaseModel):
    id: str
    animal: str
    input_type: str
    input_name: str
    interpretation: str
    human_translation: str
    context_meaning: str
    behavioral_insight: str
    timestamp: str

class AnalysisRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    animal_id: str
    animal_name: str
    input_type: str
    input_name: str
    interpretation: str
    human_translation: str
    context_meaning: str
    behavioral_insight: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Animal Communication Analysis System API"}

@api_router.get("/animals")
async def get_animals():
    """Get list of all animals with their data"""
    animals_list = []
    for animal_id, data in ANIMALS_DATA.items():
        animals_list.append({
            "id": animal_id,
            "name": data["name"],
            "scientific_name": data["scientific_name"],
            "image": data["image"],
            "vocalization_count": len(data["vocalizations"]),
            "expression_count": len(data["expressions"])
        })
    return {"animals": animals_list}

@api_router.get("/animals/{animal_id}")
async def get_animal(animal_id: str):
    """Get detailed data for a specific animal"""
    if animal_id not in ANIMALS_DATA:
        raise HTTPException(status_code=404, detail="Animal not found")
    return ANIMALS_DATA[animal_id]

@api_router.get("/animals/{animal_id}/vocalizations")
async def get_vocalizations(animal_id: str):
    """Get vocalizations for a specific animal"""
    if animal_id not in ANIMALS_DATA:
        raise HTTPException(status_code=404, detail="Animal not found")
    return {"vocalizations": ANIMALS_DATA[animal_id]["vocalizations"]}

@api_router.get("/animals/{animal_id}/expressions")
async def get_expressions(animal_id: str):
    """Get expressions for a specific animal"""
    if animal_id not in ANIMALS_DATA:
        raise HTTPException(status_code=404, detail="Animal not found")
    return {"expressions": ANIMALS_DATA[animal_id]["expressions"]}

@api_router.post("/analyze", response_model=AnalysisResponse)
async def analyze_communication(request: AnalysisRequest):
    """Analyze animal communication using AI"""
    if request.animal_id not in ANIMALS_DATA:
        raise HTTPException(status_code=404, detail="Animal not found")
    
    animal_data = ANIMALS_DATA[request.animal_id]
    input_type = ""
    input_name = ""
    input_description = ""
    input_context = ""
    input_meaning = ""
    
    # Get vocalization or expression data
    if request.vocalization_id:
        input_type = "vocalization"
        for v in animal_data["vocalizations"]:
            if v["id"] == request.vocalization_id:
                input_name = v["name"]
                input_description = v["description"]
                input_context = v["context"]
                break
        if not input_name:
            raise HTTPException(status_code=404, detail="Vocalization not found")
    elif request.expression_id:
        input_type = "expression"
        for e in animal_data["expressions"]:
            if e["id"] == request.expression_id:
                input_name = e["name"]
                input_meaning = e["meaning"]
                input_context = e["emotion"]
                break
        if not input_name:
            raise HTTPException(status_code=404, detail="Expression not found")
    else:
        raise HTTPException(status_code=400, detail="Either vocalization_id or expression_id is required")
    
    # Build AI prompt
    prompt = f"""You are an expert animal behaviorist and communication specialist. Analyze the following {animal_data['name']} communication signal and provide a detailed interpretation.

Animal: {animal_data['name']} ({animal_data['scientific_name']})
Communication Type: {input_type.capitalize()}
Signal: {input_name}
Context: {input_context}
{"Description: " + input_description if input_description else ""}
{"Emotional State: " + input_meaning if input_meaning else ""}
{"Additional Context: " + request.context if request.context else ""}

Please provide:
1. A direct human translation (as if the animal was speaking in English)
2. The contextual meaning behind this communication
3. Behavioral insights about why the animal might be communicating this way

Format your response as:
TRANSLATION: [The animal's message in first-person English]
CONTEXT: [What this communication means in context]
INSIGHT: [Behavioral insight]"""

    try:
        # Initialize Gemini chat
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="API key not configured")
        
        chat = LlmChat(
            api_key=api_key,
            session_id=f"analysis-{uuid.uuid4()}",
            system_message="You are an expert animal behaviorist who translates animal communications into human language."
        ).with_model("gemini", "gemini-3-flash-preview")
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        # Parse AI response
        lines = response.strip().split('\n')
        translation = ""
        context_meaning = ""
        insight = ""
        
        current_section = ""
        for line in lines:
            if line.startswith("TRANSLATION:"):
                current_section = "translation"
                translation = line.replace("TRANSLATION:", "").strip()
            elif line.startswith("CONTEXT:"):
                current_section = "context"
                context_meaning = line.replace("CONTEXT:", "").strip()
            elif line.startswith("INSIGHT:"):
                current_section = "insight"
                insight = line.replace("INSIGHT:", "").strip()
            elif current_section == "translation" and line.strip():
                translation += " " + line.strip()
            elif current_section == "context" and line.strip():
                context_meaning += " " + line.strip()
            elif current_section == "insight" and line.strip():
                insight += " " + line.strip()
        
        # Fallback if parsing fails
        if not translation:
            translation = input_meaning if input_meaning else f"I am making a {input_name} sound"
        if not context_meaning:
            context_meaning = f"This {input_type} indicates {input_context}"
        if not insight:
            insight = f"The {animal_data['name']} is communicating through {input_type}"
        
        # Create analysis record
        analysis_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc)
        
        # Store in database
        record = {
            "id": analysis_id,
            "animal_id": request.animal_id,
            "animal_name": animal_data["name"],
            "input_type": input_type,
            "input_name": input_name,
            "interpretation": response,
            "human_translation": translation.strip(),
            "context_meaning": context_meaning.strip(),
            "behavioral_insight": insight.strip(),
            "timestamp": timestamp.isoformat()
        }
        await db.analysis_records.insert_one(record)
        
        return AnalysisResponse(
            id=analysis_id,
            animal=animal_data["name"],
            input_type=input_type,
            input_name=input_name,
            interpretation=response,
            human_translation=translation.strip(),
            context_meaning=context_meaning.strip(),
            behavioral_insight=insight.strip(),
            timestamp=timestamp.isoformat()
        )
        
    except Exception as e:
        logger.error(f"AI analysis error: {str(e)}")
        # Provide fallback response using predefined data
        analysis_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc)
        
        fallback_translation = input_meaning if input_meaning else f"I am communicating through {input_name}"
        fallback_context = f"This {input_type} in {animal_data['name']}s typically indicates {input_context}"
        fallback_insight = input_description if input_description else f"{animal_data['name']}s use this communication pattern in specific social or survival contexts"
        
        return AnalysisResponse(
            id=analysis_id,
            animal=animal_data["name"],
            input_type=input_type,
            input_name=input_name,
            interpretation=f"Analysis based on predefined behavioral data for {animal_data['name']}",
            human_translation=fallback_translation,
            context_meaning=fallback_context,
            behavioral_insight=fallback_insight,
            timestamp=timestamp.isoformat()
        )

@api_router.get("/analysis/history")
async def get_analysis_history(limit: int = 20):
    """Get recent analysis history"""
    records = await db.analysis_records.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
    return {"history": records}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    return status_checks

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
