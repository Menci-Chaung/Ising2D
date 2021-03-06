# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import random
import numpy as np

# <codecell>

def initialize(nlist,L,N):                    
    for i in xrange(0,N):
        nlist[i][0] = (i-1)%N
        nlist[i][1] = (i-L)%N
        nlist[i][2] = (i+1)%N
        nlist[i][3] = (i+L)%N   

# <codecell>

def wolff_step(spin,nlist,N,Padd):
    
    stack = np.zeros(N)   # duzelt
    js = random.randrange(0,N)
    stack[0] = js
    sp=1
    
    oldspin=spin[js]
    newspin = -1*spin[js]
    spin[js] = newspin
    cluster_size=0
    
    while sp:
        sp = sp - 1
        current = stack[sp]
        for i in xrange (4):
            if spin[nlist[current][i]] == oldspin: 
                if random.uniform(0, 1) < Padd :
                    stack[sp] = nlist[current][i]
                    sp = sp + 1 
                    spin[nlist[current][i]] = newspin
                    cluster_size = cluster_size + 1
                    
    return cluster_size

# <codecell>

def measure(spin,nlist,N,Nobs):
    
    observable=np.zeros(Nobs)
    
    observable[0] = np.abs((1.0* np.sum(spin) / N)   )                                                                         # magnetization 
    observable[1] = -1.0* np.sum(spin[i]* (spin[nlist[i][0]] + spin[nlist[i][1]]) for i in xrange (0,N) ) / N          # energy
    observable[2] = observable[0]**2                                                                                   # m^2
    observable[3] = observable[1]**2                                                                                   # e^2    
    
    return observable

# <codecell>

def load_observable1(Nsw,J,L,H,filename,Nobs):
    
    obs=np.zeros([Nobs, Nsw])
    
    k = open('%s/observable_J%.5f_L%i_H%.2f' %(filename , J, L,H), 'r')
    
    for a in xrange(0,Nsw):
        for i in xrange(0,Nobs):
            obs[i][a]=k.readline()

    return obs

# <codecell>

def autocorrelation(Nsw,J,L,N,H,filename,Nobs):
    
    autocorrelation= [[] for i in xrange(Nobs)] 
    
    observable=load_observable1(Nsw,J,L,H,filename,Nobs)
    
    for i in xrange(0,Nobs):
        
        fm=np.fft.rfft(observable[i][:]-np.mean(observable[i][:]))/np.sqrt(len(observable[i][:]))

        fm2=np.abs(fm)**2

        cm=np.fft.irfft(fm2, len(observable[i][:])) 
        
        cm_2= cm / cm[0]
        
        autocorrelation[i] = cm_2
    
        
    np.savetxt('%s/autocorrelation/autocorrelation_fnct_magnet_J%.5f_L%i_H%.2f' %(filename,J,L,H), autocorrelation[0])    
    np.savetxt('%s/autocorrelation/autocorrelation_fnct_energy_J%.5f_L%i_H%.2f' %(filename,J,L,H), autocorrelation[1])    
    np.savetxt('%s/autocorrelation/autocorrelation_fnct_magnet2_J%.5f_L%i_H%.2f' %(filename,J,L,H), autocorrelation[2])    
    np.savetxt('%s/autocorrelation/autocorrelation_fnct_energy2_J%.5f_L%i_H%.2f' %(filename,J,L,H), autocorrelation[3])  

# <codecell>

def correlation_time(J,L,H,filename,Nobs):
    
    correlation = np.zeros(Nobs) 
    
    autocorrelation= [[] for i in xrange(Nobs)]  
      
    autocorrelation[0]=np.loadtxt('%s/autocorrelation/autocorrelation_fnct_magnet_J%.5f_L%i_H%.2f' %(filename,J,L,H))    
    autocorrelation[1]=np.loadtxt('%s/autocorrelation/autocorrelation_fnct_energy_J%.5f_L%i_H%.2f' %(filename,J,L,H))    
    autocorrelation[2]=np.loadtxt('%s/autocorrelation/autocorrelation_fnct_magnet2_J%.5f_L%i_H%.2f' %(filename,J,L,H))    
    autocorrelation[3]=np.loadtxt('%s/autocorrelation/autocorrelation_fnct_energy2_J%.5f_L%i_H%.2f' %(filename,J,L,H))  

    
    for i in xrange(0,Nobs):
        log_cm_2 =[]
        
        j=0
        
        while autocorrelation[i][j] > 0 :        
            log_cm_2.append(np.log(autocorrelation[i][j]))
            j = j+1
        
        x = np.linspace(0,len(log_cm_2)-1,len(log_cm_2))
        p = np.polyfit(x,log_cm_2,1)
        
        #log_cm_2 = np.log(cm_2[:Nsw/400 +1])           
        #x = np.linspace(0,Nsw/400,Nsw/400 +1)   
        #p = np.polyfit(x,log_cm_2,1)
    
        tau = -1 / p[0] 

        correlation[i] = 2*int(np.ceil(tau))
        
    print correlation
    
    corr_time = int(max(correlation[i] for i in xrange(0,Nobs)))
    
    k_handle = file('%s/correlation_times' %filename, 'a')
    np.savetxt(k_handle, np.column_stack(np.append([J,H,L], corr_time)),fmt='%20.2e')
    k_handle.close()
    
    return corr_time

# <codecell>

def blocking_seperating(darray,block_size):
    
    Nblock = len(darray) / block_size
    
    obs_blocking=np.zeros(Nblock)
    
    for i in xrange(0,Nblock):
        a=  darray[block_size*i:block_size*(i+1)]
        obs_blocking[i]= np.mean(a)
    
    return obs_blocking,Nblock

# <codecell>

def blocking_error(seperated_array,Nblock):
    
    error_blocking=np.sqrt(1.0*np.var(seperated_array)/(Nblock-1))
    
    return error_blocking

# <codecell>

def jackknife_delete_i(array,length):
    
    array_jack = [[] for k in range(length)] 
    
    mean_obs_jack = np.zeros(length)
    
    for i in xrange(0,length):
        array_jack[i] = np.delete(array,i)
        mean_obs_jack[i] = np.mean(array_jack[i][:])
    
    return mean_obs_jack

# <codecell>

def jackknife_error(resampled_array,mean,length):
    sigma_jack= np.sqrt(            np.sum(         pow(    (resampled_array[i]-mean),2   ) for i in xrange(0,length)   )                       )
    
    return sigma_jack

# <codecell>

def specific_heat(mean_energy,mean_energy2,J,N):
    spec_heat=1.0*J*J*N*(    mean_energy2   -   pow(  mean_energy,2  )    )
    return spec_heat

# <codecell>

def magnetic_susceptibility(mean_magnet,mean_magnet2,J,N):
    suscept=   J*N*(     mean_magnet2  -   pow(  mean_magnet,2  )    )
    return suscept

# <codecell>

def ising2dmc(J,L,N,H,Nsw,max_correlation,filename,spin_read_filename,spin_write_filename,Nobs):
    #  J = J(interaction energy) * beta(= 1/kT)  
    # H external uniform magnetic field
    
    spin =  np.loadtxt('%s' %spin_read_filename) 

    nlist = np.zeros([N,4], dtype=np.int64)

    Padd= 1 - np.exp(-2*J)
    
    initialize(nlist,L,N)

    datafile = file('%s/observable_J%.5f_L%i_H%.2f' %(filename, J,L,H), 'a')
        
    cluster=0
       
    #observable=measure(spin,nlist,N,Nobs)
    
    #np.savetxt(datafile, observable)

    for i in xrange(1,Nsw+1):
        for j in xrange(1,max_correlation+1):
            for k in xrange(1,N+1):
                a=wolff_step(spin,nlist,N,Padd)
                cluster = cluster + a
                observable=measure(spin,nlist,N,Nobs)
                np.savetxt(datafile, observable)
        
    mean_cluster = 1.0 * cluster / (Nsw*max_correlation*N*N)
    
    np.savetxt('%s' %spin_write_filename,spin)
    
    a_handle = file('%s/cluster_size' %filename, 'a')

    np.savetxt(a_handle, np.column_stack(np.append([J, H, L], mean_cluster)) , fmt='%19.5e')

    a_handle.close()

    datafile.close()

# <codecell>

def analyze(Nobserv,observable_uncorre,length,J,L,N,H):
    
# observable hatalari

    observable_mean=np.zeros(Nobserv)

    for i in xrange(Nobserv):
        observable_mean[i]=np.mean(observable_uncorre[i])


    block_size= length/10                  

    new_observable=[ [] for i in xrange(Nobserv*2) ]

    error_observable=np.zeros(Nobserv*2)

    for i in xrange(Nobserv):
        new_observable[i],Nblock = blocking_seperating(observable_uncorre[i],block_size)
        new_observable[i+Nobserv] = jackknife_delete_i(observable_uncorre[i],length)
    
    
        error_observable[i] = blocking_error(new_observable[i],Nblock)
        error_observable[i+Nobserv] = jackknife_error(new_observable[i+Nobserv],np.mean(observable_uncorre[i]),length)


    a_handle = file('uncorrelated/mean_observable_and_error', 'a')

    np.savetxt(a_handle, np.column_stack(np.append([J, H, L], np.append(observable_mean, error_observable))) , fmt='%19.5e')

    a_handle.close()

# property hesaplanmasi

    properties=np.zeros(2)

    properties[0] = magnetic_susceptibility(observable_mean[0],observable_mean[2],J,N)          # magnetic suscept
    properties[1] = specific_heat(observable_mean[1],observable_mean[3],J,N)                    # specific heat

# property hatalari
    
    error_properties=np.zeros(Nobserv)

    a=np.zeros(Nblock)
    b=np.zeros(Nblock)

    for i in xrange(0,Nblock):
        a[i]=magnetic_susceptibility(new_observable[0][i],new_observable[2][i],J,N)
        b[i]=specific_heat(new_observable[1][i],new_observable[3][i],J,N)

    error_properties[0]=blocking_error(a,Nblock)
    error_properties[1]=blocking_error(b,Nblock)


    c=np.zeros(length)
    d=np.zeros(length)
    
    for i in xrange(length):
        c[i]=magnetic_susceptibility(new_observable[0+Nobserv][i],new_observable[2+Nobserv][i],J,N)
        d[i]=specific_heat(new_observable[1+Nobserv][i],new_observable[3+Nobserv][i],J,N)

    error_properties[2]=jackknife_error(c,properties[0],length)
    error_properties[3]=jackknife_error(d,properties[1],length)

    print properties
    print error_properties

    k_handle = file('uncorrelated/properties_and_error', 'a')
    np.savetxt(k_handle, np.column_stack(np.append([J, H, L], np.append(properties, error_properties))), fmt='%20.5e')

    k_handle.close()

# <markdowncell>
