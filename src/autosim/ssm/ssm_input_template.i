begin sierra simulation_name

  # parent file: ~/autotwin/ssm/input/bob066b/bob-1mm-5kg-helmet2-0305-hemi-066b.i
  # parent file: ~/autotwin/ssm/input/bob067/bob067.i
  # parent file: ~/autotwin/ssm/input/bob068/bob-1mm-5kg-helmet2-0305-hemi-068.i
  # parent file: ~/autotwin/ssm/input/a001/a001.i
  # parent file: ~/autotwin/ssm/input/sr4c.i
  # parent file: ~/autotwin/ssm/input/IXI012-HH-1211-T1_small/ssm_input.i

  # ------------------------------------
  # units: grams, centimeters, seconds
  # -----

  # ---------------------------------------------------------------------------
  # constants
  # -----------------
  # foo = { foo = sqrt(2.0)/2.0 }
  # experiment_angle = {experiment_angle = 45}

  # ---------------------------------------------------------------------------
  # include files
  # -----------------

  # ---------------------------------------------------------------------------
  # direction vectors
  # -----------------

  define point origin with coordinates 0.0 0.0 0.0
  define point cg with coordinates 0.0 0.0 0.0

  define direction x_positive with vector 1.0 0.0 0.0
  define direction y_positive with vector 0.0 1.0 0.0
  define direction z_positive with vector 0.0 0.0 1.0

  define axis x_axis with point origin direction x_positive 
  define axis y_axis with point origin direction y_positive
  define axis z_axis with point origin direction z_positive

  # define axis cg_rotation_axis with point cg direction x_positive
  define axis cg_rotation_axis with point cg direction z_positive

  define direction adir with vector 1.0 0.0 0.0
  define direction bdir with vector {0.0} {cosd( experiment_angle )} {sind(experiment_angle)}
  define direction cdir with vector {0.0} {-sind( experiment_angle )} {cosd(experiment_angle)}

  # ---------------------------------------------------------------------------
  # user functions 
  # --------------

  {include("../../../../autotwin/ssm/bcs/shell_rotation.txt")}

  # -------------------------------
  # Define using named vector components
  begin function velocity_mag
    type = analytic
    expression variable: V = nodal_vector velocity
    evaluate expression = "sqrt((V_x)^2 + (V_y)^2 + (V_z)^2 )"
  end

  # Define using named vector components
  begin function disp_mag
    type = analytic
    expression variable: U = nodal_vector displacement
    evaluate expression = "sqrt((U_x)^2 + (U_y)^2 + (U_z)^2 )"
  end

  # ---------------------------------------------------------------------------
  # materials: listed in alphabetical order
  # ---------
  # Assumed 'ssm' repo cloned to path ~/autotwin/ssm parallel path to
  # the, e.g., ~/scratch/ixi/sim/IXI012-HH-1211-T1_small/ folder

  {include("../../../../autotwin/ssm/material/bone.txt")}
  {include("../../../../autotwin/ssm/material/csf.txt")}
  {include("../../../../autotwin/ssm/material/whitematter.txt")}

  begin rigid body rigidSkull

    # reference location = 33.6315 21.4892 12.3570
    # reference location = cg  # did not work
    # reference location = 7.55 9.25 7.75 # a001
    reference location = 0.0 0.0 0.0

    # magnitude = 1000.0
    # direction = y_positive
    # angular velocity = 1570.0 # 90 deg rotation at t=0.001
    # angular velocity = 1000.0
    # cylindrical axis = cg_rotation_axis

  end rigid body rigidSkull
  
  begin solid section rigidSection
    rigid body = rigidSkull
  end solid section rigidSection

  # ---------------------------------------------------------------------------
  # mesh
  # ----

  begin finite element model crush

    # database name = ../../geometry/bob-1mm-5kg-helmet2-hemi.g
    # database name = ../../geometry/a001/a001.e.1.0
    # database name = ../../geometry/a001/a001.e
    # database name = ../../geometry/a001/a001.e
    # database name = ../../geometry/sphere/spheres_resolution_2.exo
    # database name = ../../geometry/sphere/sr2/spheres_resolution_2.exo
    # database name = ~/autotwin/ssm/geometry/sphere/sr2/spheres_resolution_2.exo
    # database name = ../../geometry/sr4c/conf_0.1cm.g
    # database name = ../../geometry/ixi/IXI012-HH-1211-T1_small/IXI012-HH-1211-T1_small.exo
    # DATABASE_NAME
    database type = exodusII

    # ---------------
    # material blocks
    # ---------------

    # ------------------------
    begin parameters for block block_1 # bone (outer shell)

      material = bone
      model = elastic
      # model = elastic_plastic
      section = rigidSection

    end parameters for block block_1
    # ------------------------
    begin parameters for block block_2 # CSF (intermediate shell)

      material = csf
      model = elastic

    end parameters for block block_2
    # ------------------------
    begin parameters for block block_3 # white matter (inner sphere)

      material = whitematter
      model = viscoelastic_swanson

    end parameters for block block_3
    # ------------------------

  end finite element model crush

  # ---------------------------------------------------------------------------
  # procedures
  # ----------

  begin presto procedure presto_procedure

    # ------------
    # time control
    # ------------

    begin time control
  
      begin time stepping block phase_1

        start time = 0.000 # second

        begin parameters for presto region presto_region
          time step scale factor = 1.0 # unitless
        end parameters for presto region presto_region

      end time stepping block phase_1

      # termination time = 0.0001 # second
      # termination time = 0.001 # second
      # termination time = 0.006 # second
      # termination time = 0.008 # second
      # termination time = 0.010 # second
      # termination time = 0.012 # second
      # termination time = 0.020 # second
      # termination time = 0.025 # second
      # termination time = 0.035 # second
      # termination time = 0.040 # second
      # termination time = 0.100 # second
      # TERMINATION_TIME

    end time control

    # -------------
    # presto region
    # -------------

    begin presto region presto_region

      use finite element model crush

      # ----------------------
      # to locate combined shell and sphere properties
      # ----------------------
      begin mass properties
        block = block_1 block_2 block_3 
        structure name = blocks_assembly
      end mass properties

      # --------------------

       begin prescribed rotational velocity
         rigid body = rigidSkull
         # block = block_1
         # cylindrical axis = cg_rotation_axis
         # component = x
         component = z
         # function = skull_rotate
         function = shell_rotation
         # scale factor = -1.0 # radians/sec
         scale factor = 1.0 # radians/sec
       end prescribed rotational velocity

      # -------------------------------
      begin results output field_exodus

        database name = output_field.e
        database type = exodusII
      # at time 0.0 increment = 0.00002 # seconds
      # at time 0.0 increment = 0.0001 # seconds
      # at time 0.0 increment = 0.0002 # seconds
        at time 0.0 increment = 0.001  # seconds
      # at time 0.0 increment = 0.010  # seconds
 
        # ----------
        # kinematics
        # ----------
          nodal variables   = coordinates    as x
          nodal variables   = displacement   as displvec
          nodal variables   = velocity       as v

        # ------
        # stress
        # ------
          element variables = von_mises          # real 
          element variables = hydrostatic_stress # real
          element variables = fluid_pressure     # real

        # ------
        # strain
        # ------
          element variables = min_principal_log_strain  # real
          element variables = max_principal_log_strain  # real
          element variables = max_shear_log_strain      # real
        # element variables = min_principal_green_lagrange_strain # real
        # element variables = max_principal_green_lagrange_strain # real
        #
        # -----------
        # strain rate
        # -----------
          element variables = min_principal_rate_of_deformation # real
          element variables = max_principal_rate_of_deformation # real
        # element variables = min_principal_green_lagrange_strain_rate # real
        # element variables = max_principal_green_lagrange_strain_rate # real

        # ----
        # misc
        # ----
        # element variables = overlap_volume_ratio
        # element variables = death_status as dead_or_alive

        # ----------
        # invariants
        # ----------
        # element variables = e_vm     # real, von Mises of GL strain
        # element variables = e_dot_vm # real, von Mises of GL strain rate

        # ------
        # energy
        # ------
          global variables  = timestep         as ts
          global variables  = contact_energy   as ce
          global variables  = external_energy  as ee
          global variables  = internal_energy  as ie
          global variables  = kinetic_energy   as ke
          global variables  = hourglass_energy as hge # check this is near zero
          global variables  = strain_energy    as se
          global variables  = momentum         as mo

      end results output field_exodus


      # -------------------------------
      begin user output

        include all blocks

        # compute nodal speed1 as function velocity_mag
        compute nodal foobar as function disp_mag

        # compute global  g0 as interpolation of nodal displacement at point { 0. * foo} { 0. * foo} 0.
        # compute global  g1 as interpolation of nodal displacement at point { 1. * foo} { 1. * foo} 0.
        # compute global  g2 as interpolation of nodal displacement at point { 2. * foo} { 2. * foo} 0.
        # compute global  g3 as interpolation of nodal displacement at point { 3. * foo} { 3. * foo} 0.
        # compute global  g4 as interpolation of nodal displacement at point { 4. * foo} { 4. * foo} 0.
        # compute global  g5 as interpolation of nodal displacement at point { 5. * foo} { 5. * foo} 0.
        # compute global  g6 as interpolation of nodal displacement at point { 6. * foo} { 6. * foo} 0.
        # compute global  g7 as interpolation of nodal displacement at point { 7. * foo} { 7. * foo} 0.
        # compute global  g8 as interpolation of nodal displacement at point { 8. * foo} { 8. * foo} 0.
        # compute global  g9 as interpolation of nodal displacement at point { 9. * foo} { 9. * foo} 0.
        # compute global g10 as interpolation of nodal displacement at point {10. * foo} {10. * foo} 0.
        # compute global g11 as interpolation of nodal displacement at point {11. * foo} {11. * foo} 0.
        # compute global g12 as interpolation of nodal displacement at point {12. * foo} {12. * foo} 0.

        # compute global  h0 as magnitude of global  g0
        # compute global  h1 as magnitude of global  g1
        # compute global  h2 as magnitude of global  g2
        # compute global  h3 as magnitude of global  g3
        # compute global  h4 as magnitude of global  g4
        # compute global  h5 as magnitude of global  g5
        # compute global  h6 as magnitude of global  g6
        # compute global  h7 as magnitude of global  g7
        # compute global  h8 as magnitude of global  g8
        # compute global  h9 as magnitude of global  g9
        # compute global h10 as magnitude of global g10
        # compute global h11 as magnitude of global g11
        # compute global h12 as magnitude of global g12
      end

      # -------------------------------
      begin heartbeat output hscth_file

        stream name = history.csv
        format = SpyHis
      # at time 0.0 increment = 0.00002    # seconds, 50,000 Hz acquisition
      # at time 0.0 increment = 0.00003    # seconds, 33,333 Hz acquisition
        at time 0.0 increment = 0.0001     # seconds, 10,000 Hz acquisition
      # at time 0.0 increment = 0.00025    # seconds,  4,000 Hz acquisition
      # at time 0.0 increment = 0.0005     # seconds,  2,000 Hz acquisition
      # at time 0.0 increment = 0.001      # seconds,  1,000 Hz acquisition

        # -----------------------------
        # deformable body
        # -----------------------------

        # nodal displacement nearest location { 0. * foo} { 0. * foo} 0. as  u0
        # nodal displacement nearest location { 1. * foo} { 1. * foo} 0. as  u1
        # nodal displacement nearest location { 2. * foo} { 2. * foo} 0. as  u2
        # nodal displacement nearest location { 3. * foo} { 3. * foo} 0. as  u3
        # nodal displacement nearest location { 4. * foo} { 4. * foo} 0. as  u4
        # nodal displacement nearest location { 5. * foo} { 5. * foo} 0. as  u5
        # nodal displacement nearest location { 6. * foo} { 6. * foo} 0. as  u6
        # nodal displacement nearest location { 7. * foo} { 7. * foo} 0. as  u7
        # nodal displacement nearest location { 8. * foo} { 8. * foo} 0. as  u8
        # nodal displacement nearest location { 9. * foo} { 9. * foo} 0. as  u9
        # nodal displacement nearest location {10. * foo} {10. * foo} 0. as u10
        # nodal displacement nearest location {11. * foo} {11. * foo} 0. as u11
        # nodal displacement nearest location {12. * foo} {12. * foo} 0. as u12

        #nodal foobar nearest location { 0. * foo} { 0. * foo} 0. as  u0
        #nodal foobar nearest location { 1. * foo} { 1. * foo} 0. as  u1
        #nodal foobar nearest location { 2. * foo} { 2. * foo} 0. as  u2
        #nodal foobar nearest location { 3. * foo} { 3. * foo} 0. as  u3
        #nodal foobar nearest location { 4. * foo} { 4. * foo} 0. as  u4
        #nodal foobar nearest location { 5. * foo} { 5. * foo} 0. as  u5
        #nodal foobar nearest location { 6. * foo} { 6. * foo} 0. as  u6
        #nodal foobar nearest location { 7. * foo} { 7. * foo} 0. as  u7
        #nodal foobar nearest location { 8. * foo} { 8. * foo} 0. as  u8
        #nodal foobar nearest location { 9. * foo} { 9. * foo} 0. as  u9
        #nodal foobar nearest location {10. * foo} {10. * foo} 0. as u10
        #nodal foobar nearest location {11. * foo} {11. * foo} 0. as u11
        #nodal foobar nearest location {12. * foo} {12. * foo} 0. as u12

        nodal foobar nearest location  0.  0.  0. as  u0
        nodal foobar nearest location  1.  0.  0. as  u1
        nodal foobar nearest location  2.  0.  0. as  u2
        nodal foobar nearest location  3.  0.  0. as  u3
        nodal foobar nearest location  4.  0.  0. as  u4
        nodal foobar nearest location  5.  0.  0. as  u5
        nodal foobar nearest location  6.  0.  0. as  u6
        nodal foobar nearest location  7.  0.  0. as  u7
        nodal foobar nearest location  8.  0.  0. as  u8
        nodal foobar nearest location  9.  0.  0. as  u9
        nodal foobar nearest location 10.  0.  0. as u10
        nodal foobar nearest location 11.  0.  0. as u11
        nodal foobar nearest location 12.  0.  0. as u12

        element max_principal_log_strain nearest location  0.  0.  0. as  e0
        element max_principal_log_strain nearest location  1.  0.  0. as  e1
        element max_principal_log_strain nearest location  2.  0.  0. as  e2
        element max_principal_log_strain nearest location  3.  0.  0. as  e3
        element max_principal_log_strain nearest location  4.  0.  0. as  e4
        element max_principal_log_strain nearest location  5.  0.  0. as  e5
        element max_principal_log_strain nearest location  6.  0.  0. as  e6
        element max_principal_log_strain nearest location  7.  0.  0. as  e7
        element max_principal_log_strain nearest location  8.  0.  0. as  e8
        element max_principal_log_strain nearest location  9.  0.  0. as  e9
        element max_principal_log_strain nearest location 10.  0.  0. as e10
        element max_principal_log_strain nearest location 11.  0.  0. as e11
        element max_principal_log_strain nearest location 12.  0.  0. as e12

        element max_principal_rate_of_deformation nearest location  0.  0.  0. as  d0
        element max_principal_rate_of_deformation nearest location  1.  0.  0. as  d1
        element max_principal_rate_of_deformation nearest location  2.  0.  0. as  d2
        element max_principal_rate_of_deformation nearest location  3.  0.  0. as  d3
        element max_principal_rate_of_deformation nearest location  4.  0.  0. as  d4
        element max_principal_rate_of_deformation nearest location  5.  0.  0. as  d5
        element max_principal_rate_of_deformation nearest location  6.  0.  0. as  d6
        element max_principal_rate_of_deformation nearest location  7.  0.  0. as  d7
        element max_principal_rate_of_deformation nearest location  8.  0.  0. as  d8
        element max_principal_rate_of_deformation nearest location  9.  0.  0. as  d9
        element max_principal_rate_of_deformation nearest location 10.  0.  0. as d10
        element max_principal_rate_of_deformation nearest location 11.  0.  0. as d11
        element max_principal_rate_of_deformation nearest location 12.  0.  0. as d12

        global external_energy  as ee
        global internal_energy  as ie
        global kinetic_energy   as ke
        global hourglass_energy as hge # check this is near zero
        global strain_energy    as se

      end heartbeat output hscth_file

      begin heartbeat output rigid_body_file

        stream name = history_rigid.csv
        format = SpyHis
      # at time 0.0 increment = 0.00002    # seconds, 50,000 Hz acquisition
      # at time 0.0 increment = 0.00003    # seconds, 33,333 Hz acquisition
        at time 0.0 increment = 0.0001     # seconds, 10,000 Hz acquisition
      # at time 0.0 increment = 0.00025    # seconds,  4,000 Hz acquisition
      # at time 0.0 increment = 0.0005     # seconds,  2,000 Hz acquisition

        # -----------------------------
        # rigid body
        # -----------------------------

        global displx_rigidSkull
        global disply_rigidSkull
        global displz_rigidSkull
        global velx_rigidSkull
        global vely_rigidSkull
        global velz_rigidSkull
        global ax_rigidSkull
        global ay_rigidSkull
        global az_rigidSkull
        global rotdx_rigidSkull
        global rotdy_rigidSkull
        global rotdz_rigidSkull
        global rotvx_rigidSkull
        global rotvy_rigidSkull
        global rotvz_rigidSkull
        global rotax_rigidSkull
        global rotay_rigidSkull
        global rotaz_rigidSkull

      end heartbeat output rigid_body_file

      # See SSM User Guide v4.50, Section 9.6.1 Restart Options, page 777/988
      # Here is the most basic restart: restart data is written at the 
      # last step of analysis or if SSM detects an internal error, such as 
      # element inversion.
      #
      # begin restart data restart_data
      #   database name = g.rsout  # the restart file
      #   at wall time 700m increment = 12h  # 700 m = 11 hours 40 minutes
      #   restart = auto
      # end restart data restart_data

    end presto region presto_region

  end presto procedure presto_procedure

  # ---------------------------------------------------------------------------
  # end
  # ---

end sierra simulation_name

