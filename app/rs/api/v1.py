from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_rs():
    return "rs app created!"
