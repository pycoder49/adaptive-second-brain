from fastapi import APIRouter, HTTPException, Depends, Response, status


router = APIRouter(
    tags=["Documents"],
)