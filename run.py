import asyncio
import sys

async def main():
    backend_process = await asyncio.create_subprocess_exec(
        sys.executable, '-m', 'uvicorn', 'backend.app.main:app', '--reload'
    )
    
    frontend_process = await asyncio.create_subprocess_exec(
        sys.executable, '-m', 'streamlit', 'run', 'frontend/dashboard.py', '--browser.gatherUsageStats=false'
    )

    await asyncio.gather(
        backend_process.wait(),
        frontend_process.wait()
    )

if __name__ == '__main__':
    asyncio.run(main())