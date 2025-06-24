# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from typing import Optional
# from simulate import run_simulation

# app = FastAPI()

# # Allow all origins (for Flutter app access)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Use ["http://localhost:port"] in production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Input model for the simulation
# class SimulationInput(BaseModel):
#     current: float
#     cycles: int
#     mode: str
#     sei_model: Optional[str] = None
#     x_variable: str
#     y_variable: str

# # Simulation endpoint
# @app.post("/simulate")
# async def simulate(input: SimulationInput):
#     try:
#         result = run_simulation(
#             current=input.current,
#             cycles=input.cycles,
#             mode=input.mode,
#             sei_model=input.sei_model,
#             x_variable=input.x_variable,
#             y_variable=input.y_variable,
#         )
#         return result
#     except Exception as e:
#         return {"error": f"Server error: {str(e)}"}
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from simulate import run_simulation

app = FastAPI()

# Allow all origins (for Flutter app access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Input model for the simulation
class SimulationInput(BaseModel):
    current: float
    cycles: int
    mode: str
    sei_model: Optional[str] = None
    x_variable: str
    y_variable: str

# Simulation endpoint
@app.post("/simulate")
async def simulate(input: SimulationInput):
    try:
        result = run_simulation(
            current=input.current,
            cycles=input.cycles,
            mode=input.mode,
            sei_model=input.sei_model,
            x_variable=input.x_variable,
            y_variable=input.y_variable,
        )
        return result
    except Exception as e:
        return {"error": f"Server error: {str(e)}"}

# 🔧 This block ensures correct port is used when deployed on Render
if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))  # Render sets the $PORT environment variable
    uvicorn.run("main:app", host="0.0.0.0", port=port)
