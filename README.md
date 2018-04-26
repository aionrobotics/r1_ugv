# r1_ugv

**docs -**
        Mass properties data for each mesh, exported from SolidWorks.


**r1_description -**
        The model mesh files
        The URDFs
        Rviz launch file, to visualize the robot model and play with the joints


**r1_gazebo -**
        A .gazebo config file which defines the skid-steer controller and other dynamics properties for the rover in Gazebo
        The Gazebo launch file which brings up the rover in Gazebo (in the WillowGarage world ... might take some time to load at first launch)

        
**r1_teleop -**
        A simple teleop node for an Xbox controller so you can drive the rover around in Gazebo to test dynamics props/the skid-steer controller
        The teleop launch file which brings up the teleop node and Joy to read from the controller


Once your catkin workspace is built, run either of the following to see the model:

```roslaunch r1_description display.launch```

```roslaunch r1_gazebo gazebo.launch```
