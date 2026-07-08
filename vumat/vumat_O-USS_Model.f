!************************************************************************
!
! User material subroutine (VUMAT) for the large-deformation, 
! viscoelastic behavior of compressible, elastomeric foams. 
! This VUMAT is for use with the Dynamic/Explicit step in 
! Abaqus/Explicit. This VUMAT is not for use in plane stress or in 
! any other situation in which there are more strain terms than 
! stress terms.
!
! Anastasia Tzoumaka, November 2025
!
!
!************************************************************************
! Usage:
!************************************************************************
!
!     This VUMAT is based on the publication:
!     " Development and validation of subjectspecific 3D human head models 
!     based on a nonlinear visco-hyperelastic constitutive framework"
!     Kshitiz Upadhyay et al., 2022, https://doi.org/10.1098/rsif.2022.0561
!
!     Material Properties Vector (*user material, constants = 6)
!     --------------------------------------------------------------
!     Ginf      = props(1)  ! Ground-state shear modulus (kPa)
!     Kbulk     = props(2)  ! Bulk modulus (GPa)
!     alpha     = props(3)  ! Tesnion/compression asymmetry param (non-dim)
!     k11       = props(4)  ! Maxwell element viscosity (Pa s)
!     k21       = props(5)  ! Maxwell element viscosity (Pa s)
!     c21       = props(6)  ! Non-dim parameter in the viscous potential
!
!************************************************************************
      subroutine vumat(
      ! Read only (unmodifiable)variables -
     +  nblock, ndir, nshr, nstatev, nfieldv, 
     +  nprops, jInfoArray,stepTime, totalTime, 
     +  dtArray, cmname, coordMp, charLength,props,
     +  density, strainInc, relSpinInc,
     +  tempOld, stretchOld, defgradOld, 
     +  fieldOld,stressOld, stateOld, 
     +  enerInternOld, enerInelasOld,tempNew,
     +  stretchNew, defgradNew, fieldNew,
      ! Write only (modifiable) variables -
     +  stressNew, stateNew, enerInternNew, enerInelasNew )
C
      include 'vaba_param.inc'
C
      dimension props(nprops), density(nblock), coordMp(nblock,*),
     +  charLength(nblock),dtArray(2*(nblock)+1), 
     +  strainInc(nblock,ndir+nshr), relSpinInc(nblock,nshr), 
     +  tempOld(nblock), stretchOld(nblock,ndir+nshr),
     +  defgradOld(nblock,ndir+nshr+nshr),
     +  fieldOld(nblock,nfieldv), stressOld(nblock,ndir+nshr),
     +  stateOld(nblock,nstatev), enerInternOld(nblock),
     +  enerInelasOld(nblock), tempNew(nblock),
     +  stretchNew(nblock,ndir+nshr),
     +  defgradNew(nblock,ndir+nshr+nshr),
     +  fieldNew(nblock,nfieldv),
     +  stressNew(nblock,ndir+nshr), stateNew(nblock,nstatev),
     +  enerInternNew(nblock), enerInelasNew(nblock), jInfoArray(*)
      !
C
      character*80 cmname
C
            !
      ! Variables defined and used in the VUMAT
      !
      integer i,j,km,kl,stat
      !
      real*8 F_t(3,3),F_tau(3,3),Fv_t(3,3),Fv_tau(3,3),
     +  T_tau(3,3),strain_eq_Old,strain_eq_New,Fdot(3,3),
     +  properties(nprops),U_tau(3,3),U_t(3,3),stress(3,3),
     +  U_tau_inv(3,3),det_U,R_tau(3,3)
      !
      real*8 zero,one,two,half,pi,three,third
      parameter(zero=0.d0,one=1.d0,two=2.d0,half=0.5d0,Pi=3.141592653d0,
     +     three=3.d0,third=1.d0/3.d0)      
C      
      ! Initialization
      !
      properties = props
      dtime = dtArray(1)
      stress = zero

      do km = 1,nblock

          ! Copy the old and new deformation gradients into F_t and F_tau,
          !  respectively. The subscript tau denotes the time at the 
          !  end of the increment, while t denotes the time at the 
          !  beginning of the increment.
          !
          ! Copy the old and new deformation gradients into F_t and 
          !   F_tau, respectively.
          !
          F_t(1,1) = defgradOld(km,1)
          F_t(2,2) = defgradOld(km,2)
          F_t(3,3) = defgradOld(km,3)
          F_t(1,2) = defgradOld(km,4)
          !
          F_tau(1,1) = defgradNew(km,1)
          F_tau(2,2) = defgradNew(km,2)
          F_tau(3,3) = defgradNew(km,3)
          F_tau(1,2) = defgradNew(km,4)
          !
          U_t(1,1) = stretchOld(km,1)
          U_t(2,2) = stretchOld(km,2)
          U_t(3,3) = stretchOld(km,3)
          U_t(1,2) = stretchOld(km,4)
          !
          U_tau(1,1) = stretchNew(km,1)
          U_tau(2,2) = stretchNew(km,2)
          U_tau(3,3) = stretchNew(km,3)
          U_tau(1,2) = stretchNew(km,4)  

          IF (nshr .eq. one) THEN
            !
            F_t(2,3) = zero
            F_t(3,1) = zero
            F_t(2,1) = defgradOld(km,5)
            F_t(3,2) = zero
            F_t(1,3) = zero

            F_tau(2,3) = zero
            F_tau(3,1) = zero
            F_tau(2,1) = defgradNew(km,5)
            F_tau(3,2) = zero
            F_tau(1,3) = zero
            !
            U_t(2,3) = zero
            U_t(3,1) = zero
            U_t(2,1) = U_t(1,2)
            U_t(3,2) = zero
            U_t(1,3) = zero
            !
            U_tau(2,3) = zero
            U_tau(3,1) = zero
            U_tau(2,1) = U_tau(1,2)
            U_tau(3,2) = zero
            U_tau(1,3) = zero
            !
          ELSE
            F_t(2,3) = defgradOld(km,5)
            F_t(3,1) = defgradOld(km,6)
            F_t(2,1) = defgradOld(km,7)
            F_t(3,2) = defgradOld(km,8)
            F_t(1,3) = defgradOld(km,9)
            !
            F_tau(2,3) = defgradNew(km,5)
            F_tau(3,1) = defgradNew(km,6)
            F_tau(2,1) = defgradNew(km,7)
            F_tau(3,2) = defgradNew(km,8)
            F_tau(1,3) = defgradNew(km,9)
            !
            U_t(2,3) = stretchOld(km,5)
            U_t(3,1) = stretchOld(km,6)
            U_t(2,1) = U_t(1,2)
            U_t(3,2) = U_t(2,3)
            U_t(1,3) = U_t(3,1)
            !
            U_tau(2,3) = stretchNew(km,5)
            U_tau(3,1) = stretchNew(km,6)
            U_tau(2,1) = U_tau(1,2)
            U_tau(3,2) = U_tau(2,3)
            U_tau(1,3) = U_tau(3,1)
            !
            ! Form the Fdot matrix
            Fdot(1,1) = (F_tau(1,1) - F_t(1,1))/dtime
            Fdot(2,2) = (F_tau(2,2) - F_t(2,2))/dtime
            Fdot(3,3) = (F_tau(3,3) - F_t(3,3))/dtime
            Fdot(1,2) = (F_tau(1,2) - F_t(1,2))/dtime
            
            Fdot(2,3) = (F_tau(2,3) - F_t(2,3))/dtime
            Fdot(3,1) = (F_tau(3,1) - F_t(3,1))/dtime
            Fdot(2,1) = (F_tau(2,1) - F_t(2,1))/dtime
            Fdot(3,2) = (F_tau(3,2) - F_t(3,2))/dtime
            Fdot(1,3) = (F_tau(1,3) - F_t(1,3))/dtime
          ENDIF           
          !
          ! Perform the constitutive upgrade for the OUSS model
          !
          call OUSS(properties,nprops,totalTime,stepTime,dtime,
     +       F_tau,F_t,Fdot,T_tau,E_GL,stat)
        !
        ! 
        ! Update the stress
        !	
        ! Update the stress measure, (R^T) T R, used by Abaqus/Explicit
        !
        call matInv3D(U_tau,U_tau_inv,det_U,istat)
        R_tau = matmul(F_tau,U_tau_inv)
        stress = matmul(matmul(transpose(R_tau),T_tau),R_tau)
        !
        do kl = 1,ndir
          stressNew(km,kl) = stress(kl,kl)
        end do
        !
        if (nshr.ne.0) then
          stressNew(km,ndir+1) = stress(1,2)
          if (nshr.ne.1) then
            stressNew(km,ndir+2) = stress(2,3)
            if (nshr.ne.2) then
              stressNew(km,ndir+3) = stress(1,3)
            end if
          end if
        end if
      enddo
        return
      end

!************************************************************************
!     Material subroutines
!************************************************************************

      subroutine OUSS(props,nprops,total_time,step_time,dtime,
     +       F_tau,F_t,Fdot,T_tau,E_GL,stat)

      implicit none
      !
      integer i,j,k,l,m,n,nprops,stat
      !
      real*8 props(nprops),dtime,F_tau(3,3),T_tau(3,3),
     +  Iden(3,3),Ginf,Kbulk,alpha,k11,k21,c21,lam_bar1,
     +  detF,Finv(3,3),FT(3,3),FinvT(3,3),B_tau(3,3),Dmat0(3,3),
     +  B_dis(3,3),I1bar,I2bar,Fe_tr(3,3),tr_Cdis_sq,Fdot(3,3),
     +  Re_tr(3,3),Ue_tr(3,3),Ee_tr(3,3),trEe_tr,Ee0_tr(3,3),Cdot(3,3),
     +  C_tau(3,3),B_eig(3,1),B_vec(3,3),expdtDv(3,3),tmp,Dmat(3,3),
     +  T_tau_v_iso(3,3),mu_inf,C_dis(3,3), total_time,step_time,
     +  T_tau_vol(3,3), T_tau_h_iso(3,3),cmp,F_t(3,3),detA,trBDB_mat,A10,
     +  Amat(3,3),Amatinv(3,3),trDmat,BDB_mat_dis(3,3),Dmat_dis(3,3),
     +  BDB_mat0(3,3),B_BDB_mat_dis(3,3), BDB_B_mat_dis(3,3),BD_tot_dis(3,3),
     +  trBD_tot_dis,BD_tot0(3,3), F_tau_dis(3,3), Fdot_dis(3,3), Cdot_dis(3,3),
     +  Cdot_dis_2(3,3), CCdot_dis_2(3,3), J5_bar, T_tau_h_iso_n(3,3),Lmat0(3,3),
     +  B_vec_inv(3,3), detBvec, E_GL(3,3),Cdis_sq(3,3), vc1, vc2,Finv_dis(3,3),
     +  lam_bar2, lam_bar3, four, dummy_Th(3,3), I1_three, eps,Lmat(3,3),
     +  T_tau_v2_iso(3,3), T_tau_v1_iso(3,3),trBDB_mat_dis, Jdot, trLmat,
     +  avg_term,lam_bar(3,1),ci(3,1),Ndyad(3,3)
     !
      real*8 zero,one,two,three,fourth,third,half
      parameter(zero=0.d0,one=1.d0,two=2.d0,three=3.d0,fourth=1.d0/4.d0,
     +     third=1.d0/3.d0,half=1.d0/2.d0, four=4.d0, eps = 1e-8)
 
      ! Identity matrix
      !
      call onem(Iden)

      ! Obtain material properties from input file
      !
      mu_inf    = props(1)  ! Ground-state shear modulus (kPa)
      Kbulk     = props(2)  ! Bulk modulus (GPa)
      alpha     = props(3)  ! Tesnion/compression asymmetry param (non-dim)
      k11       = props(4)  ! Maxwell element viscosity (Pa s)
      k21       = props(5)  ! Maxwell element viscosity (Pa s)
      c21       = props(6)  ! Non-dim parameter in the viscous potential
      
C-------------------------------------------------------------------
C            FOR THE INITIAL DUMMY STEP 
C            RETURN WITH APPROPRIATE VALUES
C            CORRESPONDING ELASTIC RESPONSE ONLY
C-------------------------------------------------------------------
      !
      !
	    if ((total_time.eq.zero).and.(step_time.eq.zero)) then

          call matInv3D(F_tau,Finv,detF,stat)
          !
          T_tau_vol = half*Kbulk*(detF - 1/detF)*Iden
          B_tau = matmul(F_tau,transpose(F_tau))
          B_dis = (detF**(-two/three))*B_tau
          call spectral(B_dis,B_eig,B_vec,stat)
          !
          T_tau_h_iso_n = 0.0d0
          !
          avg_term = zero
          do i = 1,3
            lam_bar(i,1) = dsqrt(B_eig(i,1))
            avg_term = avg_term + lam_bar(i,1)**alpha
          end do
          !
          cmp = (two*mu_inf/alpha)/detF
          !
          T_tau_h_iso_n = zero
          do i = 1,3
            ci(i,1) = cmp*(lam_bar(i,1)**alpha - avg_term)
            do j = 1,3
              do k = 1,3
                T_tau_h_iso_n(j,k) = T_tau_h_iso_n(j,k) + ci(i,1)*B_vec(j,i)*B_vec(k,i)
                Ndyad(j,k) = B_vec(j,i)*B_vec(k,i)
              end do
            end do
          end do
          !
          T_tau = T_tau_vol + T_tau_h_iso_n 
          !   
          return

	    endif      
      
      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
      ! Compute the volumetric contribution to the Cauchy stress
      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
      !
      ! Compute the determinant, the transpose, the inverse, 
      !  and the inverse transpose of the deformation gradient
      !
      call matInv3D(F_tau,Finv,detF,stat)
      FT = transpose(F_tau)
      FinvT = transpose(Finv)
      F_tau_dis = F_tau*detF**(-one/three)
      !
      ! Compute the the volumetric part of the Cauchy stress
      ! Equation (3.7) 
      T_tau_vol = half*Kbulk*(detF - 1/detF)*Iden
      !
      B_tau = matmul(F_tau,transpose(F_tau))
      B_dis = (detF**(-two/three))*B_tau
      C_tau = matmul(transpose(F_tau),F_tau)
      C_dis = (detF**(-two/three))*C_tau
      !
      E_GL = half*(C_tau - Iden)
      !
      call spectral(B_dis,B_eig,B_vec,stat)
      !
      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
      ! Compute the hyperelastic contribution to the Cauchy stress
      ! Based on Equation (3.8)
      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
      !
      !
      avg_term = zero
      do i = 1,3
        lam_bar(i,1) = dsqrt(B_eig(i,1))
        avg_term = avg_term + lam_bar(i,1)**alpha
      end do
      !
      ! Ogden coefficient
      cmp = (two*mu_inf/alpha)/detF
      !
      ! Initialize the hyperelastic Cauchy stress
      T_tau_h_iso_n = zero
      do i = 1,3
        ci(i,1) = cmp*(lam_bar(i,1)**alpha - avg_term)
        do j = 1,3
          do k = 1,3
            T_tau_h_iso_n(j,k) = T_tau_h_iso_n(j,k) + ci(i,1)*B_vec(j,i)*B_vec(k,i)
            Ndyad(j,k) = B_vec(j,i)*B_vec(k,i)
          end do
        end do
      end do
      !
      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
      ! Compute the vsicous contribution to the Cauchy stress
      ! Based on Equation (3.9)
      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
      ! Compute the left Cauchy-Green tensor,
      ! the distortional left Cauchy-Green tensor, 
      ! and its first invariant
      I1bar = C_dis(1,1) + C_dis(2,2) + C_dis(3,3)
      !
      Cdis_sq = matmul(C_dis,C_dis)
      tr_Cdis_sq = Cdis_sq(1,1) + Cdis_sq(2,2) + Cdis_sq(3,3)
      I2bar = half*(I1bar**two - tr_Cdis_sq)
      !
      Dmat = half*(matmul(Fdot,Finv)+transpose(matmul(Fdot,Finv))) 
      !
      ! Calculate the trace of the D matrix
      trDmat = Dmat(1,1) + Dmat(2,2) + Dmat(3,3) 
      !
      Lmat = matmul(Fdot,Finv)
      trLmat = Lmat(1,1) + Lmat(2,2) + Lmat(3,3)
      !
      !   
      Fdot_dis = detF**(-one/three)*(Fdot - F_tau*trDmat/three) 
      !
      Finv_dis = detF**(-one/three)*Finv  
      !
      Dmat_dis = half*(matmul(Fdot_dis,Finv_dis)+
     + transpose(matmul(Fdot_dis,Finv_dis)))
      !
      ! Calculate the BDB matrix
      BDB_mat_dis = matmul(B_dis,matmul(Dmat_dis,B_dis))
      trBDB_mat_dis = BDB_mat_dis(1,1) + BDB_mat_dis(2,2) + BDB_mat_dis(3,3)
      !
      ! Calculate the dev( BDB )
      BDB_mat0 = BDB_mat_dis - (one/three)*trBDB_mat_dis*Iden
      !
      !!!!! Calculate the 1st viscous term in viscous Cauchy stress !!!!!
      ! Calculate coef.1
      vc1 = (1/detF)*8.d0*k11*dsqrt(max(I1bar - three + eps,zero)) 
      T_tau_v1_iso = vc1*BDB_mat0
      !
      !!!!! Calculate the 2nd viscous term in viscous Cauchy stress !!!!!
      !
      ! Calculate the B*BDB
      B_BDB_mat_dis = matmul(B_dis,BDB_mat_dis)
      !
      ! Calculate the BDB*B
      BDB_B_mat_dis = matmul(BDB_mat_dis,B_dis)
      !
      ! Calculate the dev( B*BDB + BDB*B )
      BD_tot_dis = B_BDB_mat_dis + BDB_B_mat_dis
      trBD_tot_dis = BD_tot_dis(1,1) + BD_tot_dis(2,2) + BD_tot_dis(3,3)
      BD_tot0 = BD_tot_dis - (one/three)*trBD_tot_dis*Iden
      !
      Cdot_dis = matmul(transpose(Fdot_dis),F_tau_dis) + 
     + matmul(transpose(F_tau_dis),Fdot_dis)
      Cdot_dis_2 = matmul(Cdot_dis,Cdot_dis)
      CCdot_dis_2 = matmul(C_dis,Cdot_dis_2)
      J5_bar = CCdot_dis_2(1,1) + CCdot_dis_2(2,2) + CCdot_dis_2(3,3)
      !
      !
      ! Calculate coef.2
      vc2 = (1/detF)*four*k21*J5_bar**(c21-one)*dsqrt(max(I2bar - three + eps,zero)) 
      !
      !!!!! Calculate the 2nd viscous term in viscous Cauchy stress !!!!!
      T_tau_v2_iso = vc2*BD_tot0
      !
      ! Total stress based on Equation (3.6)
      T_tau = T_tau_h_iso_n + T_tau_vol + T_tau_v1_iso + T_tau_v2_iso
      !
      return
      end subroutine OUSS 
      
!****************************************************************************
!     The next subroutine calculates various kinematical quantities
!      associated with the deformation gradient
!****************************************************************************

      subroutine skinem(F,R,U,E,istat)
      !
      ! This subroutine performs the right polar decomposition
      !  F = RU of the deformation gradient F into a rotation
      !  R and the right stretch tensor U.  The logarithmic 
      !  strain E = ln(U) is also returned.
      !
      !	F(3,3):       the deformation gradient; input
      !	detF:         the determinant of F; detF > 0
      !	R(3,3):       the rotation matrix; output
      !	U(3,3):       the right stretch tensor; output
      !	Uinv(3,3):    the inverse of U
      !	C(3,3):       the right Cauchy-Green tensor
      !	omega(3):     the squares of the principal stretches
      ! Ueigval(3):   the principal stretches
      !	eigvec(3,3):  matrix of eigenvectors of U
      !	E(3,3):       the logarithmic strain tensor; output
      ! istat:        success flag, istat=0 for a failed attempt; output
      !
      implicit none
      !
      integer istat
      !
      real*8 F(3,3),C(3,3),omega(3),Ueigval(3),eigvec(3,3),
     +  U(3,3),E(3,3),Uinv(3,3),R(3,3),detF
     

      !	Store the identity matrix in R, U, and Uinv
      !
      call onem(R)
      call onem(U)
      call onem(Uinv)
      

      ! Store the zero matrix in E
      !
      call zerom(E)
      

      ! Check if the determinant of F is greater than zero.
      !  If not, then print a diagnostic and cut back the 
      !  time increment.
      !
      call mdet(F,detF)
      if (detF.le.0.d0) then
        write(*,'(/5X,A/)') '--problem in kinematics-- the',
     +       ' determinant of F is not greater than 0'
        istat = 0
        return
      end if
      

      ! Calculate the right Cauchy-Green tensor C
      !
      C = matmul(transpose(F),F)
      
 
      ! Calculate the eigenvalues and eigenvectors of C
      !
      call spectral(C,omega,eigvec,istat)
      

      ! Calculate the principal values of U and E
      !
      Ueigval(1) = dsqrt(omega(1))
      Ueigval(2) = dsqrt(omega(2))
      Ueigval(3) = dsqrt(omega(3))
      !
      U(1,1) = Ueigval(1)
      U(2,2) = Ueigval(2)
      U(3,3) = Ueigval(3)
      !
      E(1,1) = dlog(Ueigval(1))
      E(2,2) = dlog(Ueigval(2))
      E(3,3) = dlog(Ueigval(3))
      

      ! Calculate the complete tensors U and E
      !
      U = matmul(matmul(eigvec,U),transpose(eigvec))
      E = matmul(matmul(eigvec,E),transpose(eigvec))
      

      ! Calculate Uinv
      !
      call matInv3D(U,Uinv,detF,istat)
      

      ! calculate R
      !
      R = matmul(F,Uinv)
      

      return
      end subroutine skinem

!****************************************************************************
!     The following subroutines calculate the spectral
!      decomposition of a symmetric 3 by 3 matrix
!****************************************************************************

      subroutine spectral(A,D,V,istat)
      !
      ! This subroutine calculates the eigenvalues and eigenvectors of
      !  a symmetric 3 by 3 matrix A.
      !
      ! The output consists of a vector D containing the three
      !  eigenvalues in ascending order, and a matrix V whose
      !  columns contain the corresponding eigenvectors.
      !
      implicit none
      !
      integer np,nrot,i,j,istat
      parameter(np=3)
      !
      real*8 D(3),V(3,3),A(3,3),E(3,3)


      E = A
      !
      call jacobi(E,3,np,D,V,nrot,istat)
      call eigsrt(D,V,3,np)
	

      return
      end subroutine spectral
	
!****************************************************************************

      subroutine jacobi(A,n,np,D,V,nrot,istat)
      !
      ! Computes all eigenvalues and eigenvectors of a real symmetric
      !  matrix A, which is of size n by n, stored in a physical
      !  np by np array.  On output, elements of A above the diagonal
      !  are destroyed, but the diagonal and sub-diagonal are unchanged
      !  and give full information about the original symmetric matrix.
      !  Vector D returns the eigenvalues of A in its first n elements.
      !  V is a matrix with the same logical and physical dimensions as
      !  A whose columns contain, upon output, the normalized
      !  eigenvectors of A.  nrot returns the number of Jacobi rotation
      !  which were required.
      !
      ! This subroutine is taken from 'Numerical Recipes.'
      !
      implicit none
      !
      integer ip,iq,n,nmax,np,nrot,i,j,istat
      parameter (nmax=100)
      !
      real*8 A(np,np),D(np),V(np,np),B(nmax),Z(nmax),
     +  sm,tresh,G,T,H,theta,S,C,tau
     
      
      ! Initialize V to the identity matrix
      !
      call onem(V)
      
      
      ! Initialize B and D to the diagonal of A, and Z to zero.
      !  The vector Z will accumulate terms of the form T*A_PQ as
      !  in equation (11.1.14)
      !
      do ip = 1,n
        B(ip) = A(ip,ip)
        D(ip) = B(ip)
        Z(ip) = 0.d0
      end do
      
      
      ! Begin iteration
      !
      nrot = 0
      do i=1,50
          !
          ! Sum off-diagonal elements
          !
          sm = 0.d0
          do ip=1,n-1
            do iq=ip+1,n
	            sm = sm + dabs(A(ip,iq))
            end do
          end do
          !
          ! If sm = 0., then return.  This is the normal return,
          !  which relies on quadratic convergence to machine
          !  underflow.
          !
          if (sm.eq.0.d0) return
          !
          ! In the first three sweeps carry out the PQ rotation only if
          !  |A_PQ| > tresh, where tresh is some threshold value,
          !  see equation (11.1.25).  Thereafter tresh = 0.
          !
          if (i.lt.4) then
            tresh = 0.2d0*sm/n**2
          else
            tresh = 0.d0
          end if
          !
          do ip=1,n-1
            do iq=ip+1,n
              G = 100.d0*dabs(A(ip,iq))
              !
              ! After four sweeps, skip the rotation if the 
              !  off-diagonal element is small.
              !
	      if ((i.gt.4).and.(dabs(D(ip))+G.eq.dabs(D(ip)))
     +            .and.(dabs(D(iq))+G.eq.dabs(D(iq)))) then
                A(ip,iq) = 0.d0
              else if (dabs(A(ip,iq)).gt.tresh) then
                H = D(iq) - D(ip)
                if (dabs(H)+G.eq.dabs(H)) then
                  !
                  ! T = 1./(2.*theta), equation (11.1.10)
                  !
	          T =A(ip,iq)/H
	        else
	          theta = 0.5d0*H/A(ip,iq)
	          T =1.d0/(dabs(theta)+dsqrt(1.d0+theta**2.d0))
	          if (theta.lt.0.d0) T = -T
	        end if
	        C = 1.d0/dsqrt(1.d0 + T**2.d0)
	        S = T*C
	        tau = S/(1.d0 + C)
	        H = T*A(ip,iq)
	        Z(ip) = Z(ip) - H
	        Z(iq) = Z(iq) + H
	        D(ip) = D(ip) - H
	        D(iq) = D(iq) + H
	        A(ip,iq) = 0.d0
                !
                ! Case of rotations 1 <= J < P
		!		
	        do j=1,ip-1
	          G = A(j,ip)
	          H = A(j,iq)
	          A(j,ip) = G - S*(H + G*tau)
	          A(j,iq) = H + S*(G - H*tau)
	        end do
                !
                ! Case of rotations P < J < Q
                !
	        do j=ip+1,iq-1
	          G = A(ip,j)
	          H = A(j,iq)
	          A(ip,j) = G - S*(H + G*tau)
	          A(j,iq) = H + S*(G - H*tau)
	        end do
                !
                ! Case of rotations Q < J <= N
                !
	        do j=iq+1,n
                  G = A(ip,j)
	          H = A(iq,j)
	          A(ip,j) = G - S*(H + G*tau)
	          A(iq,j) = H + S*(G - H*tau)
	        end do
	        do j = 1,n
	          G = V(j,ip)
	          H = V(j,iq)
	          V(j,ip) = G - S*(H + G*tau)
	          V(j,iq) = H + S*(G - H*tau)
	        end do
	        nrot = nrot + 1
              end if
	    end do
	  end do
          !
          ! Update D with the sum of T*A_PQ, and reinitialize Z
          !
	  do ip=1,n
	    B(ip) = B(ip) + Z(ip)
	    D(ip) = B(ip)
	    Z(ip) = 0.d0
	  end do
	end do


      ! If the algorithm has reached this stage, then there
      !  are too many sweeps.  Print a diagnostic and cut the 
      !  time increment.
      !
      write (*,'(/1X,A/)') '50 iterations in jacobi should never happen'
      istat = 0
      

      return
      end subroutine jacobi
	
!****************************************************************************

      subroutine eigsrt(D,V,n,np)
      !
      ! Given the eigenvalues D and eigenvectors V as output from
      !  jacobi, this subroutine sorts the eigenvales into ascending
      !  order and rearranges the colmns of V accordingly.
      !
      ! The subroutine is taken from 'Numerical Recipes.'
      !
      implicit none
      !
      integer n,np,i,j,k
      !
      real*8 D(np),V(np,np),P
      

      do i=1,n-1
	k = i
	P = D(i)
	do j=i+1,n
	  if (D(j).ge.P) then
	    k = j
	    P = D(j)
	  end if
	end do
	if (k.ne.i) then
	  D(k) = D(i)
	  D(i) = P
	  do j=1,n
	    P = V(j,i)
	    V(j,i) = V(j,k)
	    V(j,k) = P
	  end do
  	end if
      end do
      

      return
      end subroutine eigsrt

!****************************************************************************
!     Utility subroutines
!****************************************************************************

      subroutine matInv3D(A,A_inv,det_A,istat)
      !
      ! Returns A_inv, the inverse and det_A, the determinant
      ! Note that the det is of the original matrix, not the
      ! inverse
      !
      implicit none
      !
      integer istat
      !
      real*8 A(3,3),A_inv(3,3),det_A,det_A_inv


      istat = 1
      
      det_A = A(1,1)*(A(2,2)*A(3,3) - A(3,2)*A(2,3)) -
     +        A(2,1)*(A(1,2)*A(3,3) - A(3,2)*A(1,3)) +
     +        A(3,1)*(A(1,2)*A(2,3) - A(2,2)*A(1,3))
      
      if (det_A .le. 0.d0) then
        write(*,*) 'WARNING: subroutine matInv3D:'
        write(*,*) 'WARNING: det of mat=',det_A
        istat = 0
        return
      end if
          
      det_A_inv = 1.d0/det_A
        
      A_inv(1,1) = det_A_inv*(A(2,2)*A(3,3)-A(3,2)*A(2,3))
      A_inv(1,2) = det_A_inv*(A(3,2)*A(1,3)-A(1,2)*A(3,3))
      A_inv(1,3) = det_A_inv*(A(1,2)*A(2,3)-A(2,2)*A(1,3))
      A_inv(2,1) = det_A_inv*(A(3,1)*A(2,3)-A(2,1)*A(3,3))
      A_inv(2,2) = det_A_inv*(A(1,1)*A(3,3)-A(3,1)*A(1,3))
      A_inv(2,3) = det_A_inv*(A(2,1)*A(1,3)-A(1,1)*A(2,3))
      A_inv(3,1) = det_A_inv*(A(2,1)*A(3,2)-A(3,1)*A(2,2))
      A_inv(3,2) = det_A_inv*(A(3,1)*A(1,2)-A(1,1)*A(3,2))
      A_inv(3,3) = det_A_inv*(A(1,1)*A(2,2)-A(2,1)*A(1,2))
      

      return
      end subroutine matInv3D

!****************************************************************************

      subroutine mdet(A,det)
      !
      ! This subroutine calculates the determinant
      ! of a 3 by 3 matrix [A]
      !
      implicit none
      !
      real*8  A(3,3),det


      det = A(1,1)*A(2,2)*A(3,3) 
     +	  + A(1,2)*A(2,3)*A(3,1)
     +	  + A(1,3)*A(2,1)*A(3,2)
     +	  - A(3,1)*A(2,2)*A(1,3)
     +	  - A(3,2)*A(2,3)*A(1,1)
     +	  - A(3,3)*A(2,1)*A(1,2)


      return
      end subroutine mdet

!****************************************************************************

      subroutine onem(A)
      !
      ! This subroutine stores the identity matrix in the
      ! 3 by 3 matrix [A]
      !
      implicit none
      !
      integer i,j
      !
      real*8 A(3,3)


      do i=1,3
         do j=1,3
	    if (i .eq. j) then
              A(i,j) = 1.d0
            else
              A(i,j) = 0.d0
            end if
         end do
      end do


      return
      end subroutine onem

!****************************************************************************

      subroutine zerom(A)
      !
      ! This subroutine sets all entries of a 3 by 3 matrix to zero
      !
      implicit none
      !
      integer i,j
      !
      real*8 A(3,3)
      
      
      do i=1,3
        do j=1,3
          A(i,j) = 0.d0
        end do
      end do
      
      
      return
      end subroutine zerom

!****************************************************************************
C**********************************************************************
	SUBROUTINE devm(A,ADEV)

C	THIS SUBROUTINE CALCULATES THE DEVIATORIC PART OF A
C	3 BY 3 MATRIX [A]
C**********************************************************************

	IMPLICIT NONE
	REAL*8 A(3,3),TRA,ADEV(3,3),IDEN(3,3)
	INTEGER I,J

	CALL TRACEM(A,TRA)
	CALL ONEM(IDEN)
	CALL ZEROM(ADEV)

	DO I = 1,3
	  DO J = 1,3
	    ADEV(I,J) = A(I,J) - (1.D0/3.D0)*TRA*IDEN(I,J)
	  END DO
	END DO

	RETURN
	END

C**********************************************************************
