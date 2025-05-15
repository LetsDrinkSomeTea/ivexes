"""
Functional Diff Tool

Entry point for comparing two source directories and extracting changed functions.
"""
import subprocess
import log

logger = log.get(__name__)

def diff(old_dir, new_dir):

   cmd = [
      "git", "diff",
      "-W",            # function context
      "-w",            # ignore whitespaces
      "--no-index",    # to compare folders not commits
      old_dir, new_dir
   ]
   # @@ -1390,136 +1390,135 @@ 
   # diff --git a/screen-4.5.0/termcap.c b/screen-4.5.1/termcap.c
   logger.info(f"Running: {" ".join(cmd)}")
   result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
   files = result.stdout.split("diff --git ")[1:]
   logger.info(f'{len(files)} files altered')

   return files
