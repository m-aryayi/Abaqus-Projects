import numpy as np



def distancePolar(r1,r2,theta1,theta2):
    d2 =  r1**2 + r2**2 - 2*r1*r2*np.cos(theta1-theta2)
    return np.sqrt(d2)





# Curve Geometry
angelOfCurve = 18 #degree
outerRadius = 0.3 #m
thicknessOfCurve = 0.01 #m

angelOfCurveRa = angelOfCurve*np.pi/180
innerRadius = outerRadius - thicknessOfCurve
# totalCurveLength = outerRadius*angelOfCurveRa


# Piezoelectric Geometry
numberOfPiez = 16
pithOfPiez = 0.0005 #m
thicknessOfPiez = 0.0004 #m

totalPiezCurveLength = (numberOfPiez-1)*pithOfPiez + thicknessOfPiez
totalPiezCurveAngle = totalPiezCurveLength/outerRadius
eachPiezCurveAngle = thicknessOfPiez/outerRadius
emptyAreaOfpiezAngle = (pithOfPiez-thicknessOfPiez)/outerRadius

# Piezoelectric Excition
frequncyOfPiez = 5e6 #Hz
numberOfPeriod = 4

excitionTime = numberOfPeriod/frequncyOfPiez



# Material Properties
mat1E = 20.55e9 #Pa
mat1Nu = 0.25
mat1Density = 2007


# Cacluate run time
mat1G = mat1E/(2*(1+mat1Nu))
mat1Lambda = mat1E*mat1Nu/((1+mat1Nu)*(1-2*mat1Nu))

mat1WaveSpeedTra = np.sqrt(mat1G/mat1Density)
mat1WaveSpeedLon = np.sqrt((mat1Lambda+2*mat1G)/mat1Density)


stepTimeCoef = 1.5
timeForTravelingWave = (thicknessOfCurve*2/mat1WaveSpeedLon + excitionTime)*stepTimeCoef
# round step time
formatted_x = "{:.0e}".format(timeForTravelingWave)
leadingZero = (float('1'+formatted_x[formatted_x.find('e'):]))
stepTime = np.ceil(timeForTravelingWave/leadingZero)*leadingZero



## Calculate Angel of Each Part of Partitioned Curve 
remainTheta = (angelOfCurveRa-totalPiezCurveAngle)
thetaEnd = angelOfCurveRa/2-remainTheta/2
thetaEnd = thetaEnd - eachPiezCurveAngle/2

piezCenterPoints = [(np.cos(thetaEnd)*outerRadius,
                     np.sin(thetaEnd)*outerRadius, 0),]
piezCenterTheta = [thetaEnd]

for i in range(numberOfPiez - 1):
    thetaEnd = thetaEnd - emptyAreaOfpiezAngle
    thetaEnd = thetaEnd - eachPiezCurveAngle

    piezCenterPoints.append((np.cos(thetaEnd)*outerRadius,
                             np.sin(thetaEnd)*outerRadius,0))
    piezCenterTheta.append(thetaEnd)


# Calculate The Reflection Time form Wall
endTimeMat = np.zeros((numberOfPiez,numberOfPiez)) 

for ii in range(numberOfPiez):
    for jj in range(numberOfPiez):
        d = distancePolar(outerRadius,innerRadius,
                          piezCenterTheta[ii],piezCenterTheta[jj])
        totalDistance = d + thicknessOfCurve
        totalTimePiezo = totalDistance/mat1WaveSpeedLon
        endTimeMat[ii,jj] = totalTimePiezo
        

# Dead Zone
deadZone = excitionTime*mat1WaveSpeedLon
effectiveOutRad = outerRadius - deadZone




# thetaVec = np.radians(np.linspace(-angelOfCurve*3, 
#                                   angelOfCurve*3, 400))
thetaVec = np.linspace(-totalPiezCurveAngle*1, 
                        totalPiezCurveAngle*1, 100)
radiuVec = np.linspace(innerRadius, effectiveOutRad, 100)
theta , r = np.meshgrid(thetaVec, radiuVec)


z = np.zeros(theta.shape)

for piezoEx in range(numberOfPiez):
    print('Run: ' + str(piezoEx+1))
    for piezoSig in range(numberOfPiez):

        rPiezo = outerRadius
        tPiezoEx = piezCenterTheta[piezoEx]
        tPiezoSi = piezCenterTheta[piezoSig]
     
        csvFile = 'Exe_' + str(piezoEx+1) + '_Sig_' + str(piezoSig+1) + '.csv'
        signal = np.genfromtxt(csvFile, delimiter=',')

        maxTime = min(stepTime,endTimeMat[piezoEx,piezoSig])
        for i in range(theta.shape[0]):
            for j in range(theta.shape[1]):
                rPoint = r[i,j]
                tPoint = theta[i,j]
                dPointEx = distancePolar(rPiezo,rPoint,
                                         tPiezoEx,tPoint)
                dPointSi = distancePolar(rPiezo,rPoint,
                                         tPiezoSi,tPoint)
                distTotal = dPointEx + dPointSi
                timeTotal = distTotal/mat1WaveSpeedLon
                if maxTime <= timeTotal:
                    continue
                if excitionTime >= timeTotal:
                    continue
                
                index = np.searchsorted(signal[:,0], timeTotal)
                
                if abs(signal[index,0]-timeTotal)<1e-20:
                    amp = np.abs(signal[index,1])
                else:
                    # amp = (signal[index,1]+signal[index-1,1])/2
                    kk =(timeTotal-signal[index-1,0])/(signal[index,0]-signal[index-1,0])
                    amp =  kk * (np.abs(signal[index,1])-np.abs(signal[index-1,1])) + np.abs(signal[index-1,1])
                
                z[i,j] = z[i,j] + amp


np.savetxt('aT.csv' , theta, delimiter=",")
np.savetxt('aR.csv' , r, delimiter=",")
np.savetxt('aZ.csv' , z, delimiter=",")


# import matplotlib.pyplot as plt
# values = z
# fig, ax = plt.subplots()
# a = ax.contourf(theta, r, z)

# fig.colorbar(a)
# plt.savefig('foo.png', bbox_inches='tight')
# plt.show()




# #-- Plot Ploar... -------------------------------------------
# fig, ax = plt.subplots(subplot_kw=dict(projection='polar'))
# ax.contourf(theta, r, values)

# # ax.plot(0, outerRadius/2, 'ko')

# # Set custom axis limits
# ax.set_ylim(0.28, outerRadius)
# # ax.set_theta_offset(np.pi/2)
# # ax.set_theta_direction(-1)
# # Set the theta limits
# ax.set_thetamin(-angelOfCurve/2)
# ax.set_thetamax(angelOfCurve/2)

# plt.show()
