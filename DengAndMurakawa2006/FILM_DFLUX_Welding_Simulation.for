c----------------------------------------------
c---------------FILM SUBROUTINE----------------

      SUBROUTINE FILM(H,SINK,TEMP,KSTEP,KINC,TIME,NOEL,NPT,
     1 COORDS,JLTYP,FIELD,NFIELD,SNAME,NODE,AREA)
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION H(2),TIME(2),COORDS(3), FIELD(NFIELD)
      CHARACTER*80 SNAME

      IF (TEMP.gt.773.16) Then
         H(1) = 0.231*(TEMP-500.0)-82.1
      ELSE   
         H(1) = 0.0668*(TEMP-500.0)
      END IF
      SINK = 278.17

      RETURN
      END

c----------------------------------------------
c---------------DFLUX SUBROUTINE--------------- 

      SUBROUTINE DFLUX(FLUX,SOL,KSTEP,KINC,TIME,NOEL,NPT,COORDS,
     1 JLTYP,TEMP,PRESS,SNAME)
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION FLUX(2), TIME(2), COORDS(3)
      CHARACTER*80 SNAME

c      Goldak's Theory  

       a = 0.003
       b = 0.004
       c_f = 0.0015
       c_r = 0.006

	   f_r = 0.6
	   f_f = 1.4
c	 
       r = 0.05715
       v_theta = 0.08/(r*60.0) !rad/s
       theta_arc = v_theta*time(2)
c	  
       xarc = r*cos(theta_arc)
       yarc = r*sin(theta_arc)
       zarc = 0.4
c	  
       Xf1 = coords(1)-xarc
       Yf1 = coords(2)-yarc  !Transfer Coords
       Zf = coords(3)-zarc
       Xf = Xf1*cos(theta_arc)-Yf1*sin(theta_arc)
       Yf = Xf1*sin(theta_arc)+Yf1*cos(theta_arc)  ! Rotate Coords
c	  
       Q = 931 ! Q=Current*Voltage*efficency
c	  
       IF (Yf.gt.0) Then
          heat = 1.8663241*Q*f_f/(a*b*c_f)  !1.8663241=6*sqrt(3)/(pi^(3/2))
          shapef = EXP(-3.0*(Xf)**2.0/a**2.0-3.0*(Yf)**2.0/c_f**2.0-3.0*(Zf)**2.0/b**2.0)
       ELSE   
          heat = 1.8663241*Q*f_r/(a*b*c_r)
          shapef = EXP(-3.0*(Xf)**2.0/a**2.0-3.0*(Yf)**2.0/c_r**2.0-3.0*(Zf)**2.0/b**2.0)
       END IF

       FLUX(1) = heat*shapef

      RETURN
      END