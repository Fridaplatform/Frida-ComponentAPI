from fastapi import APIRouter, HTTPException
from utils.functions import componentGeneration
from utils import schemas

router = APIRouter()

@router.post('/componentGeneration', description="Generate React.js components based on the user's given prompt")
def generate_component(request: schemas.ComponentRequest):
    '''
    Generate React.js components based on the user's given prompt

    Args:
        request: The prompt given by the user to generate the React.js component.

    Returns:
        dict: Generated component
    '''

    try:
        component = componentGeneration.generateComponent(request)
        return{'component': component}
    except Exception as e:
        raise HTTPException(status_code=500, detail=e) from e