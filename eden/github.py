import git 
import os 
import yaml

class GithubSource(object):
    def __init__(self, url, folder_path = "."):
        self.url = url
        self.folder_path = folder_path
        self.repo_foldername = self.url.split('.git')[0].split('/')[-1]
        self.config = None

    def clone(self):
        git.Git(self.folder_path).clone(self.url)
        self.root = self.folder_path + "/" + self.repo_foldername

    def nav_into_repo(self):
        os.chdir(self.root)

    def get_eden_yml(self):
        try:
            with open("eden.yml", 'r') as stream:
                self.config = yaml.safe_load(stream)
                print(self.config)
        except FileNotFoundError:
            raise FileNotFoundError('The repo does not contain an "eden.yml" file :(')

    def build(self):
        if self.config is not None:
            print('starting build...')
            for i in range(len(self.config['build'])):
                command = self.config['build'][i]
                print("Running [{}/{}]: ".format(str(i), str(len(self.config['build']))), command )
                os.system(command)

    def run(self):
        if self.config is not None:
            print('starting run...')
            for i in range(len(self.config['run'])):
                command = self.config['run'][i]
                print("Running [{}/{}]: ".format(str(i), str(len(self.config['run']))), command )
                os.system(command)

    def build_and_run(self):
        self.clone()
        self.nav_into_repo()
        self.get_eden_yml()
        self.build()
        self.run()

    