=================================
Running a benchmark in Benchpark
=================================
After installing Benchpark, select a benchmark experiment to run on a specified system type.

Create a directory for a given experiment
----------------------------------------- 
```
cd ${APP_WORKING_DIR}/workspace 
```
Set up a workspace
-----------------------------------------
```
ramble -D . workspace setup 
```

Run the experiment
-----------------------------------------
```
ramble -D . on 
```

Analyze the experiment results 
-----------------------------------------
```
ramble -D . workspace analyze 
```