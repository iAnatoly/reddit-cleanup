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
                        config.deletePosts = parser.get('RedditCleanup','deletePosts');
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
		else:
			sys.stdout.write('_')	
		sys.stdout.flush()
			
	print ""

def cleanupAll(name,ttl,callback):
	print "Cleaning up "+name
	# while (True):
	comments = callback(limit=20)
	if (comments is not None):
		try:
			nextElement,rest = comments.next()
			cleanup(itertools.chain([nextElement], rest),ttl)
		except TypeError:
			cleanup(callback(limit=200000),ttl)
		except StopIteration:
			print "Done."
			return;
	else:
		return;

config = ConfigHelper.getConfig();

client = praw.Reddit(user_agent=config.userAgent)
client.login(config.userName,config.password)


cleanupAll("Comments",config.ttlDays,client.user.get_comments)
if (config.deletePosts):
	cleanupAll("Posts",config.ttlDays,client.user.get_submitted)
