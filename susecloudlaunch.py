from cloudlaunchinstance import CloudLaunchInstance
import os


instance = CloudLaunchInstance("nat-instance")
# Clear screen
os.system('clear')
instance.user_interface()