# Abaqus-Projects

This repository contains a variety of ABAQUS projects codes. In the future, I will add more details about them and their related files.



## 
- ## List of Projects:
	- ArmitageAndOyen2017

      In this directory, the USDFLD subroutine and MATLAB have been used to simulate the below paper. Matlab file couple with Abaqus and run the input file using the subroutine.
      
      <a href="https://doi.org/10.1016/j.actbio.2016.12.036"> <i> Armitage, O. E., & Oyen, M. L. (2017). Indentation across interfaces between stiff and compliant tissues.</i> </a>
      
	- ZhouEt_al2017

      In this directory, the USDFLD subroutine has been used to simulate the below paper. The VUSDFLD subroutine is available for future simulation development in Abaqus/Explicit. If you want to use this project in a different Abaqus version, download the file and run it as below in the terminal:   

          abaqus job=Job-Validation input=Job-Validation user=USDFLD_CapModel.for
 	  
      <a href="https://doi.org/10.1016/j.powtec.2016.09.061"> <i> Zhou, M., Huang, S., Hu, J., Lei, Y., Xiao, Y., Li, B., ... & Zou, F. (2017). A density-dependent modified Drucker-Prager Cap model for die compaction of Ag57. 6-Cu22. 4-Sn10-In10 mixed metal powders.</i> </a>
