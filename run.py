import asyncio
import sys
import webbrowser
import os

async def main():
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    os.environ['FASTAPI_URL'] = 'http://localhost:8000'

    backend_process = await asyncio.create_subprocess_exec(
        sys.executable, '-m', 'uvicorn', 'backend.app.main:app', '--reload'
    )
    
    frontend_process = await asyncio.create_subprocess_exec(
        sys.executable, '-m', 'streamlit', 'run', 'frontend/dashboard.py', 
        '--browser.gatherUsageStats=false', '--server.port=8501'
    )

    await asyncio.sleep(2)
    webbrowser.open('http://localhost:8501')

    try:
        await asyncio.gather(
            backend_process.wait(),
            frontend_process.wait()
        )
    except asyncio.CancelledError:
        backend_process.terminate()
        frontend_process.terminate()
        await asyncio.gather(backend_process.wait(), frontend_process.wait())

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
