from pid import PID
from yaw_controller import YawController
from lowpass import LowPassFilter
import rospy

GAS_DENSITY = 2.858
ONE_MPH = 0.44704


class Controller(object):
    #def __init__(self, *args, **kwargs):
    def __init__(self, vehicle_mass, 
                       accel_limit, 
                       wheel_radius, 
                       fuel_capacity, 
                       brake_deadband, 
                       decel_limit, 
                       wheel_base, 
    	               steer_ratio, 
                       max_lat_accel, 
                       max_steer_angle):
        # TODO: Implement
	self.yaw_controller = YawController(wheel_base, steer_ratio, 0.1, max_lat_accel, max_steer_angle)

        kp =  0.3
        ki =  0.1
        kd = 0    
        mn = 0
        mx = 0.2 #accel_limit
        self.throttle_controller = PID(kp, ki, kd, mn, mx)

        tau = 0.5 # 1/(2pi*tau) = cutoff frequency
        ts = 0.02 #sample time 
        self.vel_lpf = LowPassFilter(tau, ts)
        
        self.vehicle_mass = vehicle_mass
        self.fuel_capacity = fuel_capacity
        self.brake_deadband = brake_deadband
        self.decel_limit = decel_limit
        self.accel_limit = accel_limit
        self.wheel_radius = wheel_radius

        self.last_time = rospy.get_time()

    #def control(self, *args, **kwargs):
        # TODO: Change the arg, kwarg list to suit your needs
        # Return throttle, brake, steer
        #return 1., 0., 0.
    def control(self, current_vel, dbw_enabled, linear_vel, angular_vel):
	# TODO: Change the arg, kwarg list to suit your needs
        # Return throttle, brake, steer
        #return 1., 0., 0.

        if not dbw_enabled:
        	self.throttle_controller.reset()
        	return 0., 0., 0.

        throttle, brake, steering = 0.0, 0.0, 0.0

        #current_vel = self.vel_lpf.filt(current_vel)

        #velocity error
        vel_error = linear_vel -current_vel
        
        current_time = rospy.get_time()
        sample_time = current_time-self.last_time

        desired_accel = self.throttle_controller.step(vel_error, sample_time)
        self.last_vel = current_vel
        self.last_time = current_time

        decel = max(vel_error, self.decel_limit)
        torque = abs(decel) * (self.vehicle_mass + self.fuel_capacity*GAS_DENSITY) * self.wheel_radius 

        if linear_vel == 0. and current_vel < 0.1:
            throttle = 0
            brake = torque

        elif desired_accel < .1 and vel_error < 0:
            throttle = 0
            brake = torque  # Torque N*m
        else:
        	throttle = desired_accel

        #rospy.logwarn("desired_accel:{0} vel_error:{1} sample_time:{2} linear_vel:{3} current_vel:{4}".format(
        #	desired_accel, vel_error, sample_time, linear_vel, current_vel ))

        steering = self.yaw_controller.get_steering(linear_vel, angular_vel, current_vel)


        return throttle, brake, steering

def reset(self):
        self.throttle_controller.reset()
