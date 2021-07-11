import git 
import os 
import yaml

from .log_utils import Colors

class GithubSource(object):
    def __init__(self, url, folder_path = "."):
        self.url = url
        self.folder_path = folder_path
        self.repo_foldername = self.url.split('.git')[0].split('/')[-1]
        self.config = None

    def clone(self):
        """
        Clones the repo specified in `self.url`
        """
        git.Git(self.folder_path).clone(self.url)
        self.root = self.folder_path + "/" + self.repo_foldername

    def nav_into_repo(self):
        """
        navigates into the repository's root folder.
        """
        os.chdir(self.root)

    def get_eden_yml(self):
        """
        Looks for the eden.yml file which contains all the 
        commands needed to build and host a block.

        Raises:
            FileNotFoundError: Raised when `eden.yml` file is not found.
        """
        try:
            with open("eden.yml", 'r') as stream:
                self.config = yaml.safe_load(stream)
        except FileNotFoundError:
            raise FileNotFoundError('The repo does not contain an "eden.yml" file :(')

    def build(self):
        """
        Runs the commands listed under the build section in the eden.yml file.
        """
        if self.config is not None:
            print('starting build...')
            for i in range(len(self.config['build'])):
                command = self.config['build'][i]
                message = "[" + Colors.CYAN+ "EDEN" +Colors.END+ "] " + Colors.GREEN + "Running [{}/{}]: ".format(str(i+1), str(len(self.config['build']))) + Colors.END
                print(message, command )
                os.system(command)

    def run(self):
        """
        Runs the commands listed under the run section in the eden.yml file.
        """
        if self.config is not None:
            for i in range(len(self.config['run'])):
                command = self.config['run'][i]
                message = "[" + Colors.CYAN+ "EDEN" +Colors.END+ "] " + Colors.GREEN + "Running [{}/{}]: ".format(str(i+1), str(len(self.config['run']))) +  Colors.END
                print(message, command )
                os.system(command)

    def build_and_run(self):
        self.clone()
        self.nav_into_repo()
        self.get_eden_yml()
        self.build()
        self.run()

    