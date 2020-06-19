from git import Repo
from git import Git
import os
from os import path
from flask import Flask, jsonify, request

import logging
app = Flask(__name__)


class AutoDeployGit:
    def __init__(self, location, git_url, repo_name, start_scripts_list=[], python_version="python3"):
        try:
            self.count_repo_check = 0
            self.location_repo = location
            self.git_url = git_url
            self.repo_name = repo_name
            self.start_scripts_list = start_scripts_list
            self.python_version = python_version
            self.init_repo()
        except Exception as e:
            logging.error(e)

    def init_repo(self):
        """ Check if it is a forever-loop """
        if self.count_repo_check <= 3:
            """ Check if it is a git-repo """
            try:
                self.repo = Repo(f"{self.location_repo}/{self.repo_name}")
            except:
                self.count_repo_check += 1
                print(self.count_repo_check)
                self.init_folder(self.location_repo)
                Git(self.location_repo).clone(self.git_url)
                self.init_repo()

    def init_folder(self, folder):
        print(path.exists(folder))
        if path.exists(folder) == False:
            os.makedirs(folder)

    def start_scripts(self):
        """ Check if there is a script """
        if len(self.start_scripts_list) > 0:
            for script in self.start_scripts_list:
                try:
                    os.system(f"{self.python_version} {script}")
                except:
                    print(f"Error script {script}")

    def pull_git(self):
        try:
            os.system('sudo rm -rf /home/pi/MCT-S4-Project-III/')
            o = self.repo.remotes.origin
            o.pull()
            os.system('cp -r /home/pi/MCT-S4-Project-III/piKeuken/. /home/pi/project3/')
            #os.system('cp /home/pi/settings.json /home/pi/MCT-S4-Project-III/piKeuken')
            print("updated")
        except Exception as e:
            logging.error(e)

#autodeploy = AutoDeployGit("/home/pi","https://github.com/StijnVandendriessche1/MCT-S4-Project-III.git", "MCT-S4-Project-III")
#autodeploy.pull_git()
#
#
# @app.route('/pull')
# def pull_git():
#     try:
#         global autodeploy
#         autodeploy.pull_git()
#         return "OK"
#     except Exception as ex:
#         logging.error(ex)
#
#
# print("hier")
# try:
#     if __name__ == '__main__':
#         app.run(host="0.0.0.0", port="5000")
# except Exception as ex:
#     logging.error(ex)
