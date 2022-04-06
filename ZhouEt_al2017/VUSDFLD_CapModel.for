      subroutine vusdfld(
c Read only -
     *   nblock, nstatev, nfieldv, nprops, ndir, nshr, 
     *   jElem, kIntPt, kLayer, kSecPt, 
     *   stepTime, totalTime, dt, cmname, 
     *   coordMp, direct, T, charLength, props, 
     *   stateOld, 
c Write only -
     *   stateNew, field )
c
      include 'vaba_param.inc'
c
      dimension jElem(nblock), coordMp(nblock,*), 
     *          direct(nblock,3,3), T(nblock,3,3), 
     *          charLength(nblock), props(nprops), 
     *          stateOld(nblock,nstatev), 
     *          stateNew(nblock,nstatev),
     *          field(nblock,nfieldv)
      character*80 cmname
c
c     Local arrays from vgetvrm are dimensioned to 
c     maximum block size (maxblk)
c
      parameter( nrData=6 )
      character*3 cData(maxblk*nrData)
      dimension rData(maxblk*nrData), jData(maxblk*nrData)
c
      jStatus = 1
      call vgetvrm( 'PEQC', rData, jData, cData, jStatus )
c
      if( jStatus .ne. 0 ) then
         call xplb_abqerr(-2,'Utility routine VGETVRM '//
     *      'failed to get variable.',0,zero,' ')
         call xplb_exit
      end if
c
      call setField( nblock, nstatev, nfieldv, nrData, 
     *   rData, stateOld, stateNew, field)
c
      return
      end
      subroutine setField( nblock, nstatev, nfieldv, nrData, 
     *   strain, stateOld, stateNew, field )
c
      include 'vaba_param.inc'
c
      dimension stateOld(nblock,nstatev), 
     *   stateNew(nblock,nstatev),
     *   field(nblock,nfieldv), strain(nblock,nrData)
c
      do k = 1, nblock
				EPS = ABS( strain(k,4) )
				ro = (2.71828**(EPS))*0.42
				field(k,1) = ro
	
c
      end do
c
      return
      end