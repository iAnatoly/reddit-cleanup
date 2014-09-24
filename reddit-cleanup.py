#!/usr/bin/python
import praw
import sys
import os
import ConfigParser;
from datetime import datetime;


class Config:
        def __init__(self):
                self.ttlDays=7;
                self.userName = '';
		self.password = '';
		self.deletePosts = True;
		self.deleteComments = True;
		self.userAgent='Paranoia/1.0';

class ConfigHelper:
        @staticmethod
        def getFileName():
                return os.path.dirname(__file__)+"/reddit-cleanup.config";
        @staticmethod
        def getConfig():
                config = Config();
                try:

                        parser = ConfigParser.ConfigParser();
                        parser.read(ConfigHelper.getFileName());

                        config.ttlDays = parser.getint('RedditCleanup','ttlDays');
                        config.userName = parser.get('RedditCleanup','userName');
                        config.password = parser.get('RedditCleanup','password');
                        config.deletePosts = parser.getboolean('RedditCleanup','deletePosts');
                        config.deleteComments = parser.getboolean('RedditCleanup','deleteComments');
                except Exception as e:
                        print "Error reading config {0}:{1}".format(ConfigHelper.getFileName(),e);
			sys.exit(-1);
                return config;


def cleanup(generator,ttl):
	for item in generator:
		whencreated = datetime.fromtimestamp(item.created);
		delta = datetime.now() - whencreated;
		if (delta.days>ttl):
			item.delete();
			sys.stdout.write('.')	
			sys.stdout.flush()
		else:
			sys.stdout.write('_')	
			sys.stdout.flush()
			
	print ""

def cleanupAll(name,ttl,callback):
	now = datetime.now();
	print "Starting clean-up for {0} at {1}".format(name,now);
	comments = callback(limit=200000);
	cleanup(comments,ttl);
	print "Done. Time taken: {0}".format(datetime.now()-now);

config = ConfigHelper.getConfig();

client = praw.Reddit(user_agent=config.userAgent)
client.login(config.userName,config.password)

if (config.deleteComments):
	cleanupAll("Comments",config.ttlDays,client.user.get_comments)
if (config.deletePosts):
	cleanupAll("Posts",config.ttlDays,client.user.get_submitted)
