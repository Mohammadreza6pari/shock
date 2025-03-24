import subprocess
from .models import Diffusion

def run_diffusion(diffusion_id):
    try:
        diffusion = Diffusion.objects.get(id=diffusion_id)
        diffusion.create_output_folder()
        result = subprocess.run(
            diffusion.cmd_arguments,
            shell=False, 
            text=True,
            capture_output=True,
            check=True
            )
        
        if Diffusion.SUCCESS_CMD_OUTPUT not in result.stdout or result.stderr:
            raise Exception(result.stderr or result.stdout)
        
        diffusion.logs = {
            "stdout": result.stdout,
        }

        diffusion.status = 'finished'
    
    except subprocess.CalledProcessError as err:
        diffusion.logs = {
            "error": str(err.stderr),
        }
        diffusion.status = 'failed'
    
    except Exception as err:
        print(f"Error occuured in run_diffusion task. {repr(err)}")
        diffusion.logs = {
            "error": str(err)
        }
        diffusion.status = 'failed'
        raise Exception("Error in run_diffusion")
    
    finally:
        diffusion.save()
        
