import numpy as np


def motion_model_spring_damper(q_prev, u, dt, msr):
    msr.m_set_joint_angles(q_prev)
    Mu = msr.m_calc_actuation_matrix()
    tau_u = Mu@u
    tau_int = -msr.m_calc_tau_int()
    tau_s = msr.m_calc_joint_force()

    q_new = q_prev + np.linalg.inv(msr.c_joints)@(tau_u + tau_int + tau_s)*dt 
    
    return q_new, tau_u, tau_int, tau_s


def simulate_magbot(data, q_init, msr):
    ## This is for checking how well the motion model works on its own. 
    # Num iterations are the length of our collected data
    iters = len(data)
    
    # Load all the relevant data 
    t = np.array(data.iloc[:, 1])/1000
    u = np.array(data.iloc[:, 2:10])

    output = np.zeros((iters, 9))
    q = q_init
    for i in range(iters):
        # Simulate magbot
        if i < iters - 1:
            dt = t[i+1] - t[i]
        q, tau_u, tau_int, tau_s = motion_model_spring_damper(q, u[i, :], dt, msr)

        # Append stuff to output data
        output[i, 0] = t[i]
        output[i, 1:3] = np.degrees(q)
        output[i, 3:5] = tau_u
        output[i, 5:7] = tau_int
        output[i, 7:9] = tau_s

    return output

def simulate_error(data, q_init, msr, std_dev):
    #This function adds random gaussian errors to each line of the recorded coil current
    #This is used to study the effect of errors in coil currents
    iters = len(data)
    
    # Load all the relevant data 
    t = np.array(data.iloc[:, 1])/1000
    u = np.array(data.iloc[:, 2:10])

    output = np.zeros((iters, 9))
    q = q_init
    for i in range(iters):
        # Simulate magbot
        if i < iters - 1:
            dt = t[i+1] - t[i]
        
        #modify coil currents
        u_mod = u[i, :] + np.random.normal(0, std_dev, size=8)

        q, tau_u, tau_int, tau_s = motion_model_spring_damper(q, u_mod, dt, msr)

        # Append stuff to output data
        output[i, 0] = t[i]
        output[i, 1:3] = np.degrees(q)
        output[i, 3:5] = tau_u
        output[i, 5:7] = tau_int
        output[i, 7:9] = tau_s

    return output

def compare(output1, output2):
    length = len(output1)
    dq = np.zeros((length, 2))

    for i in range(length):
        dq[i, :] = output2[i, 1:3] - output1[i, 1:3]
    
    dq1_mean = np.mean(np.abs(dq[:, 0]), axis=0)
    dq1_max = np.max(np.abs(dq[:, 0]), axis=0)
    dq2_mean = np.mean(np.abs(dq[:, 1]), axis=0)
    dq2_max = np.max(np.abs(dq[:, 1]), axis=0)

    return dq1_max, dq1_mean, dq2_max, dq2_mean