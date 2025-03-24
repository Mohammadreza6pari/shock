import subprocess
from .models import Diffusion

def run_diffusion(diffusion_id):
    try:
        diffusion = Diffusion.objects.get(id=diffusion_id)
        diffusion.create_output_folder()
        subprocess.run(diffusion.cmd_arguments, shell=False, check=True)
        diffusion.status = 'finished'
    
    except Exception as err:
        print(f"Error occuured in run_diffusion task. {repr(err)}")
        diffusion.status = 'failed'
        raise Exception("Error in run_diffusion")
    
    finally:
        diffusion.save()
        
