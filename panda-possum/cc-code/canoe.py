"""
Last modified by Lucas on Feb 1, 2026

This module contains the Canoe class and Loadcase class. 
Written and tested by Albert, Elorie, Folu, John, Lucas (2T6 Hull & Structural Directors), and Arthur
Used Claude Sonnet 4.5 for assistance with code optimization.
"""
import os  # Needed for get_c4 function to find c4table.txt
import math_utils 
import math as mat
import pandas as pd
import numpy as np  # Add NumPy for vectorization

class Canoe:
    def __init__(self, L=0, Lp=0, Ld=0, Lf=0, W=0, t1=0, t2=0, d=0, b=0, s=0, f=0, n=0, density=0, bowpower=4, sternpower=4):
        """Initialize canoe parameters."""
        self.Length = L
        self.Length_paddler = Lp
        self.Length_deepest = Ld
        self.Length_first = Lf
        self.Width = W
        self.smooth1 = t1
        self.smooth2 = t2
        self.depth = d
        # self.h_flange = h                                                       # Not sure what this parameter is... doesn't show up in documentation, isn't an input, and isn't used in any functions
        self.b_rocker = b
        self.s_rocker = s
        self.flare = f
        self.shape_param = n
        self.density = density
        self.bowpower = bowpower
        self.sternpower = sternpower
        self.numstations = 101
        self.increment = self.Length/(self.numstations-1)
        self.bowtol = 1e-4
        
        # Cache for control points and tables
        self._wlvalues_cache = None
        self._klvalues_cache = None
        self._control_points_cache = {}

    # Only use for backwards race cases
    def canoe_reverse(self): # Lucas, tested sucessfully                                                       
        """
        Reverses the canoe parameters for analysis of stern-first motion
        """
        self.b_rocker, self.s_rocker = self.s_rocker, self.b_rocker
        self.Length_first = self.Length - self.Length_first - self.Length_paddler
        self.Length_deepest = self.Length - self.Length_deepest
        self.smooth1, self.smooth2 = self.smooth2, self.smooth1
        return 0
    # Testing Folu
    def keelline(self, x):
        """
        Defines keel line shape (depth below top of canoe) along the length of the canoe
        """
        if x < self.Length_deepest:
            return self.depth - self.b_rocker*mat.fabs(pow((1.-x/self.Length_deepest),self.bowpower))
        else: 
            return self.depth - self.s_rocker*mat.fabs((pow((self.Length_deepest-x)/(self.Length-self.Length_deepest),self.sternpower)))

    def waterline(self, x):
        """
        Defines waterline shape along the length of the canoe
        """
        m1 = self.Width/(2*self.Length_first)
        m2 = self.Width/(2*(self.Length-self.Length_paddler-self.Length_first))
        rbow = self.Width/2 - m1*math_utils.ramp(self.Width/(2*m1),self.smooth1) - m2*math_utils.ramp(self.Width/(2*m2)-self.Length,self.smooth2)
        rstern = self.Width/2 - m1*math_utils.ramp(self.Width/(2*m1)-self.Length,self.smooth1) - m2*math_utils.ramp(self.Width/(2*m2),self.smooth2)
        waterline_soln = self.Width/2 - m1*math_utils.ramp(self.Width/(2*m1)-x,self.smooth1) - m2*math_utils.ramp(x-self.Length+self.Width/(2*m2),self.smooth2) - (rstern-rbow)*x/self.Length - rbow
        return waterline_soln

    def wl_and_kl_tables(self, numstations=101):
        """
        Computes waterline and keelline values at specified number of stations along canoe length
        Default divides canoe into 100 segments
        :param numstations: Number of stations to compute along canoe length
        """
        # Check cache first
        if self._wlvalues_cache is not None and self._klvalues_cache is not None:
            return 0
        
        # Vectorized computation
        x_values = np.linspace(0, self.Length, numstations)
        
        # Waterline vectorized
        m1 = self.Width/(2*self.Length_first)
        m2 = self.Width/(2*(self.Length-self.Length_paddler-self.Length_first))
        rbow = self.Width/2 - m1*math_utils.ramp(self.Width/(2*m1),self.smooth1) - m2*math_utils.ramp(self.Width/(2*m2)-self.Length,self.smooth2)
        rstern = self.Width/2 - m1*math_utils.ramp(self.Width/(2*m1)-self.Length,self.smooth1) - m2*math_utils.ramp(self.Width/(2*m2),self.smooth2)
        
        self.wlvalues = [self.Width/2 - m1*math_utils.ramp(self.Width/(2*m1)-x,self.smooth1) - m2*math_utils.ramp(x-self.Length+self.Width/(2*m2),self.smooth2) - (rstern-rbow)*x/self.Length - rbow for x in x_values]
        
        # Keelline vectorized
        mask_bow = x_values < self.Length_deepest
        self.klvalues = np.where(
            mask_bow,
            self.depth - self.b_rocker*np.abs(np.power((1.-x_values/self.Length_deepest), self.bowpower)),
            self.depth - self.s_rocker*np.abs(np.power((self.Length_deepest-x_values)/(self.Length-self.Length_deepest), self.sternpower))
        ).tolist()
        
        self._wlvalues_cache = self.wlvalues
        self._klvalues_cache = self.klvalues
        return 0
    
    def control_points(self, x):
        """
        Determines control points for Bezier curve at given station along the canoe hull
        :param station: Index of station along hull for iteration (x coordinate along canoe length))
        :return: Control points for curves P0y, P0z, P1y, P1z, P2y, P2z, P3y, P3z
        """
        self.wl_and_kl_tables()                     

        if x % self.increment == 0:
            w = self.wlvalues[int(x/self.increment)]
            k = self.klvalues[int(x/self.increment)]

        else:
            w = self.waterline(x)
            k = self.keelline(x)

        fmax = mat.asin(w/(2.*k))
        
        if fmax < self.flare:
            flareangle = fmax
        else: 
            flareangle = self.flare
        
        u1max = k/mat.cos(flareangle)
        u2max = w - k*mat.tan(flareangle)
        u1 = u1max*(0.25+0.75*self.shape_param)
        u2 = u2max*(0.5+0.5*self.shape_param)

        P0y = w
        P0z = 0.0
        P1y = P0y - u1*mat.sin(flareangle)
        P1z = P0z - u1*mat.cos(flareangle)
        P3y = 0.0
        P3z = -k
        P2y = P3y + u2
        P2z = P3z

        return P0y, P0z, P1y, P1z, P2y, P2z, P3y, P3z

    def analyze(self, d, theta, trim): # Lucas
        
        # Pre-allocate arrays
        areas = np.zeros(self.numstations-1)
        centroidx = np.zeros(self.numstations-1)
        centroidy = np.zeros(self.numstations-1)
        centroidz = np.zeros(self.numstations-1)

        x_values = np.arange(self.numstations-1) * self.increment
        flag = 0

        for i in range(self.numstations-1):
            P0y, P0z, P1y, P1z, P2y, P2z, P3y, P3z = self.control_points(i*self.increment)
            
            error, area_addition, centroidy_addition, centroidz_addition = math_utils.section_resultant(P0y,P0z,P1y,P1z,P2y,P2z,P3y,P3z, (d if trim == 0 else d-trim/self.Length*x_values[i]),theta)

            if error == -1:
                raise ValueError("LEAK - Section resultant caused leak in analyze function.")
            
            areas[i] = area_addition
            centroidx[i] = x_values[i]
            centroidy[i] = centroidy_addition
            centroidz[i] = centroidz_addition

        # Vectorized integration using parallelograms
        volume = np.sum((areas[1:] + areas[:-1])/2) * self.increment

        # Vectorized centroid calculation
        cenx = np.sum(centroidx * areas * self.increment) / volume
        ceny = np.sum(centroidy * areas * self.increment) / volume
        cenz = np.sum(centroidz * areas * self.increment) / volume

        return flag, volume, cenx, ceny, cenz                            # flag = 0 means no leak, flag = 1 means leak

    def find_wline(self, v_target, theta, trim): # Folu
        Maxiterations = 50                                               # defined as wlmaxit in the legacy code
        wl_tolerance = 0.0001                                            # tolerance in meters for wline calculations, if calculated value misses target value by more than the tolerance it returns -1 which would be a fail
        
        test_d = self.depth/2
        width = self.depth/2
        self.trim = trim

        if trim == 0 :
            width = self.get_bwl(0)/2
            dcheck = width * mat.tan(theta)
            [f,v,cx,cy,cz] = self.analyze(dcheck,theta,trim)
            if v< v_target:
                return -1

        width = self.depth/2

        for k in range(0, Maxiterations):                 # Note: i++ from the C++ code is just saying that 1 is added to i AFTER each iteration, rather than before, thus this translation works
            [f,v,cx,cy,cz] = self.analyze(test_d,theta,trim)
            if mat.fabs(v-v_target) < wl_tolerance:
                return test_d
            if v>v_target or f == 1:
                test_d += width/2
            else:
                test_d -= width/2
            width = width/2
        return -1
    # Testing Albert
    def moment(self, y1, z1, y2, z2, weight, theta):
        return -(mat.cos(theta)*(y2-y1) - mat.sin(theta)*(z2-z1))*weight

    def cross_curve(self, weight, cm_height): # Folu                      # cm_height is center of mass height above GUNWALE
        #tangent, tipping_angle
        tipping_tolerance = 1e-2
        theta = 0
        tinc = 0.01
        
        #calculating the tangent
        theta1 = theta
        theta2 = theta + tinc
        d1 = self.find_wline(weight, theta1, 0)
        f,v,cx,cy,cz = self.analyze(d1,theta1,0)
        moment1 = self.moment(cy,cz,0,cm_height,weight,theta)
        
        d2 = self.find_wline(weight, theta2, 0)
        f,v,cx,cy,cz = self.analyze(d2,theta2,0)
        moment2 = self.moment(cy,cz,0,cm_height,weight,theta)
        tangent = (moment2-moment1)/(theta2-theta1)

        #calculating the tipping angle
        tolerance = tipping_tolerance                              
        width = self.get_bwl(0)/2
        dtest = d1
        dmax = self.depth
        dmin = 0

        theta = mat.atan2(dtest,width)
        f,v,cx,cy,cz = self.analyze(dtest,theta,0)
        Maxiterations = 50
        count = 0
        flag = 0
        while mat.fabs(weight-v) > tolerance:
            if count >= Maxiterations:
                raise ValueError("LEAK - Cross curve tipping angle calculation did not converge.")
                # flag = 1
                # break
            count += 1
            if weight < v:
                dmin = dtest
                dtest = (dtest+dmax)/2
            else:
                dmax = dtest
                dtest = (dtest+dmin)/2
            theta = mat.atan2(dtest,width)
            f,v,cx,cy,cz = self.analyze(dtest, theta, 0)
        tipping = theta
        return flag, tipping, tangent

    def displacement_curve(self):  # Folu
        d = self.depth
        dinc = 0.01

        while d >= 0:
            f,v,cx,cy,cz = self.analyze(d, 0, 0)
            print(f"{d}\t{v}\n")
            d -= dinc

        return 0

    def spline_length(self, P0y, P0z, P1y, P1z, P2y, P2z, P3y, P3z, d):  # Lucas
        """
        Calculates length of spline curve that's underwater using control points, at a given depth
        """

        if (d > -P3z):
            return 0, 0  # Spline length and cmz will not contribute to surface area calc if the spline is entirely above water
        
        a1 = P0y - 3*P1y + 3*P2y - P3y
        b1 = 3*P1y - 6*P2y + 3*P3y
        c1 = 3*P2y - 3*P3y
        d1 = P3y

        a3 = P0z - 3*P1z + 3*P2z - P3z
        b3 = 3*P1z - 6*P2z + 3*P3z
        c3 = 3*P2z - 3*P3z
        d3 = P3z

        ti = 0                                                   # lower bound
        tf = math_utils.solver_cubic(a3, b3, c3, d3 + d - P0z)   # upper bound

        if (tf < 0):
            tf = 0			# if there's a leak we ignore the section - presumably there should not be any leaks in this routine
        
        if (d == 0):
            tf = 1
        
        tinc = 0.01
        splinelength = 0

        y1 = math_utils.spline(a1,b1,c1,d1,ti)
        z1 = math_utils.spline(a3,b3,c3,d3,ti)

        zmoment = 0

        t = ti + tinc

        while t <= tf:
            y2 = math_utils.spline(a1,b1,c1,d1,t)
            z2 = math_utils.spline(a3,b3,c3,d3,t)
            segment = mat.sqrt((y2-y1)*(y2-y1) + (z2-z1)*(z2-z1))
            splinelength += segment
            zmoment += segment*(z1+z2)/2.		# moment = length * average height
            
            y1 = y2
            z1 = z2
            
            t += tinc
        
        cmz = zmoment/splinelength

        return splinelength, cmz
    
    def surface_area(self, d): # Folu 
        
        # Pre-allocate arrays
        lengths = np.zeros(self.numstations)
        cenzs = np.zeros(self.numstations)

        for i in range(self.numstations):
            P0y, P0z, P1y, P1z, P2y, P2z, P3y, P3z = self.control_points(i*self.increment)
            lengths[i], cenzs[i] = self.spline_length(P0y,P0z,P1y,P1z,P2y,P2z,P3y,P3z,d)
        
        # Vectorized integration
        area = np.sum((lengths[1:] + lengths[:-1])/2) * self.increment * 2.0
        
        x_indices = np.arange(self.numstations) * self.increment
        areamoment = np.sum(lengths * x_indices)
        areazmoment = np.sum(cenzs * lengths)
        
        cx = areamoment / np.sum(lengths)
        cz = areazmoment / np.sum(lengths)
        
        return area, cx, cz
    # Testing Lucas
    def read_c4_table(self, c4_file):                    # C4 table is a text file stored within the panda/possum folder, used exclusively in the KAPER function
        c4table = []
        for i in range(3):
            layer = []
            for j in range(17):
                line = c4_file.readline().strip()
                values = [float(val) for val in line.split('\t')]
                layer.append(values)
            c4table.append(layer)
        return c4table
    
    def get_c4(self, Cv, Cp, vtol):                                  # moved from main.py due to usage in kaper 
        """
        Retrieves C4 value from table based on hull parameters for use in KAPER method
        """
        # Not sure if this is the way to do this -Lucas
            
        c4_path = os.path.join(os.path.dirname(__file__), 'c4table.txt')
        with open(c4_path, 'r') as c4:
            c4table = self.read_c4_table(c4)

        Cvind1 = int((Cv - 0.001)/0.0005)     
        Cvind2 = Cvind1 + 1
        if Cvind1 < 0:
            Cvind1 = 0
        elif Cvind1 > 2:
            Cvind1 = 2
        if Cvind2 < 0:
            Cvind2 = 0
        elif Cvind2 > 2:
            Cvind2 = 2

        Cpind1 = int((Cp - 0.48)/0.01)
        Cpind2 = Cpind1 + 1
        if Cpind1 < 0:
            Cpind1 = 0
        elif Cpind1 > 16:
            Cpind1 = 16
        if Cpind2 < 0:
            Cpind2 = 0
        elif Cpind2 > 16:
            Cpind2 = 16

        vtolind1 = int((vtol - 0.4)/0.1)
        vtolind2 = vtolind1 + 1
        if vtolind1 < 0:
            vtolind1 = 0
        elif vtolind1 > 13:
            vtolind1 = 13
        if vtolind2 < 0:
            vtolind2 = 0
        elif vtolind2 > 13:
            vtolind2 = 13

        cvratio, cpratio, vtolratio = 0, 0, 0
        if Cvind1 != Cvind2:
            cvratio = (Cv - (Cvind1*.0005 + .001))/(Cvind2*.0005 - Cvind1*.0005)
        if Cpind1 != Cpind2:
            cpratio = (Cp - (Cpind1*.01 + .48))/(Cpind2*.01 - Cpind1*.01)
        if vtolind1 != vtolind2:
            vtolratio = (vtol - (vtolind1*.1 + .4))/(vtolind2*.1 - vtolind1*.1)

        # 8 corners of the prism to be interpolated, a[2][2][2] array
        corners = [[[0 for _ in range(2)] for _ in range(2)] for _ in range(2)]
        for i in range(Cvind1, Cvind2 + 1):
            for j in range(Cpind1, Cpind2 + 1):
                for k in range(vtolind1, vtolind2 + 1):
                    corners[i - Cvind1][j - Cpind1][k - vtolind1] = c4table[i][j][k]          # not sure how to correctly reference c4table here -Lucas

        actual_cv = [[0 for _ in range(2)] for _ in range(2)]
        for i in range(2):
            for j in range(2):
                actual_cv[i][j] = cvratio*corners[1][i][j] + (1-cvratio)*corners[0][i][j]

        actual_cp = [0 for _ in range(2)]
        for i in range(2):
            actual_cp[i] = cpratio*actual_cv[1][i] + (1-cpratio)*actual_cv[0][i]

        c4 = vtolratio*actual_cp[1] + (1-vtolratio)*actual_cp[0]

        return c4

    def kaper(self, bwl, ewl, ws, cp, cv, lcb, disp, le, v):  # Lucas
        """
        Use of John Winter's KAPER method to calculate resistance of canoe based on hull parameters and speed

        **Inputs are in imperial units, see conversions made in get_friction function**
        Disp is in long tonnes, lengths in feet, speed in knots, LCB is a fraction of length

        :return: Resistance in pounds 
        """

        vtol = v/(mat.sqrt(ewl))                                                                             # Velocity to length ratio (Froude number)

        c1 = 0.002*mat.sqrt(bwl/ewl)*((4*vtol)**4)                                                           # Bow wave resistance factor
        c2 = 0.005 * mat.sin(le * mat.pi / 180) * ((4*vtol)**2)                                              # Stern wave resistance factor
        c3 = (1 if vtol < 1.5 else 0.7)*0.8*mat.cos(3.65*vtol+0.07) + (1 if vtol < 1.5 else 0.96)*1.2        # Speed-dependent factor
        c4 = self.get_c4(cv,cp,vtol)                                                                         # Hull-shape-dependent factor                                                                             
        c5 = (0.5/lcb)**0.35                                                                                 # LCB correction factor

        rr = (4*c5*disp*(vtol**4) + c1 + c2)*(c3*c4*c5)
        
        if (v >= 1.6 and v < 3):
            rr *= 0.75
        if (v >= 1.4 and v < 1.6):
            rr *= 0.85
        # Note: 1.6889 converts speed to feet/sec from knots, ft^2/s is used for kinematic visc, density is in slugs/ft^3
        reynold = (v*1.6889*ewl/1.08)*100000                                                                 # 1.08 is kinematic viscosity of freshwater, legacy code uses saltwater                                                          
        cf = 0.075/((mat.log10(reynold)-2)**2)                                                               # ITTC 1957 friction coefficient. Could adapt in the future to something more modern or specfiic to shallow water
        rf = 0.99525*cf*ws*((v*1.6889)**2)                                                                   # Frictional resistance in pounds, 0.99525 is density/2
        
        return rf + rr
    
    # Testing John
    def get_ewl(self, freeboard, theta, trim): # John
        """
        Effective length at waterline
        """
        areas = []

        x = 0.0
        areamax = 0.0
        xmax = 0

        for i in range(self.numstations):
            P0y, P0z, P1y, P1z, P2y, P2z, P3y, P3z = self.control_points(i*self.increment)

            if self.Length == 0:
                raise ZeroDivisionError("length must be non-zero")

            freeboard = freeboard - (trim / self.Length) * x
            status, area, yloc, zloc = math_utils.section_resultant(P0y, P0z, P1y, P1z, P2y, P2z, P3y, P3z, freeboard, theta)
            if status == -1:
                raise ValueError("LEAK detected in get_ewl calculation")
                # print("LEAK")
                # return 1.0

            areas.append(area)
            if area > areamax:
                areamax = area
                xmax = i

            x += self.increment

        xstart = 0
        for xs in range(0, xmax):
            flag = False
            denom = xmax - xs
            for i in range(xs, xmax):
                ramp = ((i - xs) / denom) * areamax  # float division
                if ramp > areas[i]:
                    flag = True
                    break
            if not flag:
                xstart = xs
                break

        xend = self.numstations - 1
        for xe in range(self.numstations - 1, xmax, -1):
            flag = False
            denom = xe - xmax
            for i in range(xe, xmax, -1):
                ramp = ((xe - i) / denom) * areamax  # float division
                if ramp > areas[i]:
                    flag = True
                    break
            if not flag:
                xend = xe
                break

        return (xend - xstart) * self.increment
    
    def get_lwl(self, freeboard): # John
        """
		Length at waterline
		"""
        flag = False
        starti = 0
        endi = 0

        self.wl_and_kl_tables()
		
        for i in range(self.numstations):
            if self.klvalues[i] > freeboard:
                flag = True
                starti = i
                break
				
        if not flag:
            return self.Length
			
        flag = False
        for i in range(self.numstations - 1, -1, -1):
            if self.klvalues[i] > freeboard:
                flag = True
                endi = i
                break

        return (endi - starti) * self.increment

			
    def get_bwl(self, freeboard):
        """
        Beam (width) at waterline
        """
        bwl = 0

        for i in range(0, self.numstations):
            P0y,P0z,P1y,P1z,P2y,P2z,P3y,P3z = self.control_points(i*self.increment)
            a3 = P0z - 3*P1z + 3*P2z - P3z
            b3 = 3*P1z - 6*P2z + 3*P3z
            c3 = 3*P2z - 3*P3z
            d3 = P3z;		
            tf = math_utils.solver_cubic(a3, b3, c3, d3+freeboard-P0z)

            a1 = P0y - 3*P1y + 3*P2y - P3y
            b1 = 3*P1y - 6*P2y + 3*P3y
            c1 = 3*P2y - 3*P3y
            d1 = P3y

            width = math_utils.spline(a1,b1,c1,d1,tf)
            if (width > bwl):
                bwl = width
        
        return bwl*2

    def get_le(self, freeboard):               # Made some changes, but things get wonky at really small freeboard (hopefully won't happen))
        """
        Entry angle in degrees.
        Note: Near the bow tip (x=0), control points can have negative P1y/P2y due to geometry formulas. This is handled by sampling slightly downstream.
        """
        TOLERANCE = self.bowtol
        xinterval = self.Length_deepest
        xpos = self.Length_deepest / 2.0

        # ---- Find entrance position ----
        if self.depth - self.b_rocker > freeboard:
            xentrance = 0.0
        else:
            flag = False
            while not flag:
                if mat.fabs(self.keelline(xpos) - freeboard) < TOLERANCE:
                    flag = True
                else:
                    if self.keelline(xpos) > freeboard:
                        xpos -= xinterval / 2.0
                    else:
                        xpos += xinterval / 2.0
                    xinterval /= 2.0
            xentrance = xpos

        dx = self.Length / 1000.0
        
        # ---- Handle bow tip case ----
        # At xentrance=0, control points are malformed (P1y, P2y < 0).
        
        if xentrance == 0.0:
            # Sample at dx and 2*dx where control points are more valid
            x1 = dx
            x2 = 2 * dx
        else:
            x1 = xentrance
            x2 = xentrance + dx

        # ---- First width ----
        P0y, P0z, P1y, P1z, P2y, P2z, P3y, P3z = self.control_points(x1)

        A3 = P0z - 3 * P1z + 3 * P2z - P3z
        B3 = 3 * P1z - 6 * P2z + 3 * P3z
        C3 = 3 * P2z - 3 * P3z
        D3 = P3z

        tf = math_utils.solver_cubic(A3, B3, C3, D3 + freeboard - P0z)

        A1 = P0y - 3 * P1y + 3 * P2y - P3y
        B1 = 3 * P1y - 6 * P2y + 3 * P3y
        C1 = 3 * P2y - 3 * P3y
        D1 = P3y

        if tf < 0:
            w1 = 0.0
        else:
            w1 = math_utils.spline(A1, B1, C1, D1, tf)

        # ---- Second width ----
        P0y, P0z, P1y, P1z, P2y, P2z, P3y, P3z = self.control_points(x2)

        A3 = P0z - 3 * P1z + 3 * P2z - P3z
        B3 = 3 * P1z - 6 * P2z + 3 * P3z
        C3 = 3 * P2z - 3 * P3z
        D3 = P3z

        tf = math_utils.solver_cubic(A3, B3, C3, D3 + freeboard - P0z)

        A1 = P0y - 3 * P1y + 3 * P2y - P3y
        B1 = 3 * P1y - 6 * P2y + 3 * P3y
        C1 = 3 * P2y - 3 * P3y
        D1 = P3y

        if tf < 0:
            w2 = 0.0
        else:
            w2 = math_utils.spline(A1, B1, C1, D1, tf)

        # ---- Entrance angle ----
        angle = mat.atan2(w2 - w1, dx)
        angle = mat.fabs(angle / mat.pi * 180.0)

        return angle

    def get_cp(self, freeboard, lwl): #Arthur
        """
        Prismatic coefficient
        """
        areamax = 0.0

        for i in range(0, self.numstations):
            P0y,P0z,P1y,P1z,P2y,P2z,P3y,P3z = self.control_points(i*self.increment)
            flag, area, y_loc, z_loc = math_utils.section_resultant(P0y, P0z, P1y, P1z, P2y, P2z, P3y, P3z, freeboard, 0)
            if flag == -1: # this in theory shouldn't happen anymore since, leaks are checked in math utils
                # print("LEAK\n")
                raise ValueError("LEAK detected in get_cp calculation")
                # return 1
            if area > areamax:
                areamax = area

        flag, v, cx, cy, cz = self.analyze(freeboard, 0, 0)
        return (v/(lwl*areamax))

    def get_cv(self, disp, lwl): # Arthur
        """
        Volumetric Coefficient
        """
        return (disp/(lwl**3))

    def get_friction(self, freeboard, v):   # Lucas
        
        flag, volume, cx, cy, cz = self.analyze(freeboard, 0, 0)
        
        if (flag == 1):
            print("LEAK - Terminating\n")
            return -1
    
        lwl = self.get_lwl(freeboard)
        bwl = self.get_bwl(freeboard)
        ewl = self.get_ewl(freeboard,0,0)
        ws, ccenx, ccenz = self.surface_area(freeboard)
        Cp = self.get_cp(freeboard,lwl)
        Cv = self.get_cv(volume,lwl)
        lcb = cx/self.Length
        disp = volume
        le = self.get_le(freeboard)

	    # Convert units just to be sure...
        
        lwl *= 3.2808399;			# metres to feet
        bwl *= 3.2808399;			# metres to feet
        ewl *= 3.2808399;			# metres to feet
        ws *= 10.7639104;			# square metres to square feet
        disp *= 0.984206528;		# cubic metres of water to long tons
        v *= 1.94384449;			# m/s to knots

        force = self.kaper(bwl,ewl,ws,Cp,Cv,lcb,disp,le,v)
        return force
    
    # Testing Lucas
    def output_mesh(self, meshout): # John
        """
        Tested somewhat without issue, need to test in context of full program to ensure it works properly -Lucas
        Outputs mesh points to meshout file in freeship format
        ** Need to input the meshout file as follows: open(file_path, "w") **
        Also make sure the file that will be written to has been created in the same location (folder) as the programprior to calling the function
        
        This or something equivalent probably has to be added to main prior to output_mesh call:
            import os
            folder = os.path.dirname(__file__)
            file_path = os.path.join(folder, 'canoe_mesh.txt')
        """
        n = 20.0
        meshout.write("0\n\n")                           # Will check for where meshout is coming from, should be creating or adding to a text file

        for i in range(self.numstations):
            x = i * self.increment

            # control_points(i, P0y, P0z, P1y, P1z, P2y, P2z, P3y, P3z)
            P0y, P0z, P1y, P1z, P2y, P2z, P3y, P3z = self.control_points(x)

            # Convert cubic Bezier control points to power basis coefficients
            A1 = P0y - 3 * P1y + 3 * P2y - P3y
            B1 = 3 * P1y - 6 * P2y + 3 * P3y
            C1 = 3 * P2y - 3 * P3y
            D1 = P3y

            A3 = P0z - 3 * P1z + 3 * P2z - P3z
            B3 = 3 * P1z - 6 * P2z + 3 * P3z
            C3 = 3 * P2z - 3 * P3z
            D3 = P3z

            for j in range(int(n) + 1):
                t = j / n  
                y = math_utils.spline(A1, B1, C1, D1, t)
                z = math_utils.spline(A3, B3, C3, D3, t)

                # x values need to be reversed for freeship
                meshout.write(f"{self.Length - x}\t{y}\t{z}\n")

            meshout.write("\n")

        meshout.write("EOF\n")
        return 0
		
    def waterplane(self, freeboard):     # Arthur
        """
        Something something waterplane stuff
        """
        self.wl_and_kl_tables()
        
        # Vectorized depth calculation
        keels = np.array(self.klvalues)
        submerged = np.maximum(keels - freeboard, 0)
        
        # Vectorized area and moment calculations
        segarea = (submerged[1:] + submerged[:-1]) / 2.0
        area = np.sum(segarea) * self.increment
        
        # Avoid division by zero
        denom = submerged[1:] + submerged[:-1]
        mask = denom != 0
        segcentroids = np.zeros(len(denom))
        segcentroids[mask] = self.increment * (np.arange(1, self.numstations)[mask] - 
                                                (2*submerged[:-1][mask] + submerged[1:][mask]) / 
                                                (3.0 * denom[mask]))
        
        first_moment = np.sum(segarea * segcentroids)
        centroid = first_moment / area * self.increment if area > 0 else 0
        
        second_moment = np.sum((segcentroids - centroid)**2 * segarea) * self.increment

        return centroid, area, second_moment

    def analyze_all(self, loadcases_array):  # Lucas                                              # It might make more sense to have this function in the main script since it uses all prior functions and uses loadcase stuff
        """
        Detailed entire analysis of canoe in various situations
        """ 
        surfacearea, cmx, cmz = self.surface_area(0)          # Will finish last due to use of all prior functions

        hull_weight = surfacearea*self.density
        hull_cmx = cmx
        hull_cmz = cmz
        actualbeam = self.get_bwl(0)
        
        error = False
        outputs = [hull_weight]

        for i in range(len(loadcases_array)):
            
            loadcases_array[i].weights_df["Actual Value"] = 0.0

            # Vectorized paddler weight calculations
            weights = loadcases_array[i].paddlers_df["weight (kg)"].values
            weightSum = np.sum(weights)
            
            if weightSum == 0:
                error = True
                print("No paddler weight detected - cannot analyze load case\n")
                continue
            
            # Vectorized center of mass calculations
            cVmlist = np.array(loadcases_array[i].vertCenterMass())
            weighted_heights = np.sum(weights * cVmlist)
            
            totweight = weightSum + hull_weight
            paddlers_cmz = weighted_heights / (weightSum*100)
            tot_cmz = ((hull_cmz*hull_weight + (paddlers_cmz - self.depth)*weightSum)/totweight)

            # Vectorized paddler center calculation
            num_paddlers = len(weights)
            if num_paddlers > 1:
                paddler_positions = self.Length_first + (np.arange(num_paddlers)/(num_paddlers-1))*self.Length_paddler
            else:
                paddler_positions = np.array([self.Length_first + 0.5*self.Length_paddler])
            
            paddlers_cmx = np.sum(weights * paddler_positions) / weightSum

            d = self.find_wline((totweight)/1000*1.0, 0, 0)
            loadcases_array[i].weights_df.loc["Freeboard","Actual Value"] = d

            if (d < 0):
                error = True
                continue

            flag_analyze,volume,cx,cy,cz = self.analyze(d,0,0)

            if flag_analyze == 1:
                error = True
                continue

            paddlercentre_ideal = (cx*volume - hull_cmx*hull_weight/1000.)/((weightSum)/1000.)
            loadcases_array[i].weights_df.loc["PaddlerCentre", "Actual Value"] = (paddlercentre_ideal - paddlers_cmx)/self.Length_paddler

            lwl = self.get_lwl(d)
            loadcases_array[i].weights_df.loc["Cp", "Actual Value"] = self.get_cp(d,lwl)
            
            friction = self.get_friction(d,2.57222222)
            if (friction < 0):
                error = True
                continue
            loadcases_array[i].weights_df.loc["Drag", "Actual Value"] = friction
            
            # Stability calculations
            flag_cross_curve, tipping, tangent = self.cross_curve(totweight/1000 * 1.0, tot_cmz)
            if flag_cross_curve == 1:
                error = True
                continue
            loadcases_array[i].weights_df.loc["Stability", "Actual Value"] = tangent
            loadcases_array[i].weights_df.loc["LeakAngle", "Actual Value"] = tipping
            
            wpcen,wparea,wpmom2 = self.waterplane(d)
            loadcases_array[i].weights_df.loc["SecondMoment", "Actual Value"] = wpmom2
            loadcases_array[i].weights_df.loc["WaterplaneCentroid", "Actual Value"] = wpcen/self.Length

            if not loadcases_array[i].back_weights_df.empty:
                loadcases_array[i].back_weights_df["Actual Value"] = 0.0
                self.canoe_reverse()
                loadcases_array[i].back_weights_df.loc["Drag", "Actual Value"] = self.get_friction(d,2.57222222)
                self.canoe_reverse()

            # Collect outputs efficiently
            outputs.extend([
                loadcases_array[i].weights_df.loc["Cp", "Actual Value"],
                loadcases_array[i].weights_df.loc["Freeboard", "Actual Value"],
                loadcases_array[i].weights_df.loc["Drag", "Actual Value"],
                loadcases_array[i].weights_df.loc["Stability", "Actual Value"],
                loadcases_array[i].weights_df.loc["LeakAngle", "Actual Value"],
                loadcases_array[i].weights_df.loc["SecondMoment", "Actual Value"],
                loadcases_array[i].weights_df.loc["WaterplaneCentroid", "Actual Value"],
                loadcases_array[i].weights_df.loc["PaddlerCentre", "Actual Value"],
                loadcases_array[i].back_weights_df.loc["Drag", "Actual Value"] if not loadcases_array[i].back_weights_df.empty else "N/A"
            ])

        return (1 if error else 0), outputs, loadcases_array, actualbeam, hull_weight, surfacearea, cmx
    
    # Testing Lucas
    def output_all(self, loadcases_array, surfacearea, hull_weight, cmx, actualbeam, canoeout): # John
        
        canoeout.write("Canoe Data\n\n")

        canoeout.write("Input Values\n\n")
        
        canoeout.write(
            "Length\tNominal Beam\tDepth\tNominal Flare Angle\tLength to Deepest Point\t"
            "Length to First Paddler\tLength of Paddlers' Box\tShape Parameter\tBow Rocker\t"
            "Stern Rocker\tArea Density\n"
        )
        canoeout.write(
            f"{self.Length}\t{self.Width}\t{self.depth}\t{self.flare}\t{self.Length_deepest}\t"
            f"{self.Length_first}\t{self.Length_paddler}\t{self.shape_param}\t{self.b_rocker}\t"
            f"{self.s_rocker}\t{self.density}\n\n"
        )

        canoeout.write("Output Values\n\n")
        canoeout.write("Surface Area\tWeight\tLCM\tActual Beam\n")
        canoeout.write(f"{surfacearea}\t{hull_weight}\t{cmx}\t{actualbeam}\n\n")

        canoeout.write("2 Men Loadcase\n")
        i = 0
        canoeout.write(
            "Cp\tFreeboard\tDrag at 5 knots\tInitial Stability\tLeak Angle\t"
            "Second Moment of Waterplane Area\tWaterplane Centroid\tPaddler Centre\tReverse Drag\n"
        )
        canoeout.write(
            f"{loadcases_array[i].weights_df.loc['Cp']}\t{loadcases_array[i].weights_df.loc['Freeboard']}\t{loadcases_array[i].weights_df.loc['Drag']}\t"
            f"{loadcases_array[i].weights_df.loc['Stability']}\t{loadcases_array[i].weights_df.loc['LeakAngle']}\t"
            f"{loadcases_array[i].weights_df.loc['SecondMoment']}\t{loadcases_array[i].weights_df.loc['WaterplaneCentroid']}\t"
            f"{loadcases_array[i].weights_df.loc['PaddlerCentre']}\t{loadcases_array[i].back_weights_df.loc['Drag']}\n\n"                         
        )

        i = 1
        canoeout.write("2 Women Loadcase\n")
        canoeout.write(
            "Cp\tFreeboard\tDrag at 5 knots\tInitial Stability\tLeak Angle\t"
            "Second Moment of Waterplane Area\tWaterplane Centroid\tPaddler Centre\tReverse Drag\n"
        )
        canoeout.write(
            f"{loadcases_array[i].weights_df.loc['Cp']}\t{loadcases_array[i].weights_df.loc['Freeboard']}\t{loadcases_array[i].weights_df.loc['Drag']}\t"
            f"{loadcases_array[i].weights_df.loc['Stability']}\t{loadcases_array[i].weights_df.loc['LeakAngle']}\t"
            f"{loadcases_array[i].weights_df.loc['SecondMoment']}\t{loadcases_array[i].weights_df.loc['WaterplaneCentroid']}\t"
            f"{loadcases_array[i].weights_df.loc['PaddlerCentre']}\t{loadcases_array[i].back_weights_df.loc['Drag']}\n\n"                         
        )

        i = 2
        canoeout.write("3 Men Loadcase\n")
        canoeout.write(
            "Cp\tFreeboard\tDrag at 5 knots\tInitial Stability\tLeak Angle\t"
            "Second Moment of Waterplane Area\tWaterplane Centroid\tPaddler Centre\tReverse Drag\n"
        )
        canoeout.write(
            f"{loadcases_array[i].weights_df.loc['Cp']}\t{loadcases_array[i].weights_df.loc['Freeboard']}\t{loadcases_array[i].weights_df.loc['Drag']}\t"
            f"{loadcases_array[i].weights_df.loc['Stability']}\t{loadcases_array[i].weights_df.loc['LeakAngle']}\t"
            f"{loadcases_array[i].weights_df.loc['SecondMoment']}\t{loadcases_array[i].weights_df.loc['WaterplaneCentroid']}\t"
            f"{loadcases_array[i].weights_df.loc['PaddlerCentre']}\t{loadcases_array[i].back_weights_df.loc['Drag']}\n\n"                              
        )

        i = 3
        canoeout.write("3 Women Loadcase\n")
        canoeout.write(
            "Cp\tFreeboard\tDrag at 5 knots\tInitial Stability\tLeak Angle\t"
            "Second Moment of Waterplane Area\tWaterplane Centroid\tPaddler Centre\tReverse Drag\n"
        )
        canoeout.write(
            f"{loadcases_array[i].weights_df.loc['Cp']}\t{loadcases_array[i].weights_df.loc['Freeboard']}\t{loadcases_array[i].weights_df.loc['Drag']}\t"
            f"{loadcases_array[i].weights_df.loc['Stability']}\t{loadcases_array[i].weights_df.loc['LeakAngle']}\t"
            f"{loadcases_array[i].weights_df.loc['SecondMoment']}\t{loadcases_array[i].weights_df.loc['WaterplaneCentroid']}\t"
            f"{loadcases_array[i].weights_df.loc['PaddlerCentre']}\t{loadcases_array[i].back_weights_df.loc['Drag']}\n\n"                                
        )

        i = 4
        canoeout.write("4 Mixed Load Case\n")
        canoeout.write(
            "Cp\tFreeboard\tDrag at 5 knots\tInitial Stability\tLeak Angle\t"
            "Second Moment of Waterplane Area\tWaterplane Centroid\tPaddler Centre\tReverse Drag\n"
        )
        canoeout.write(
            f"{loadcases_array[i].weights_df.loc['Cp']}\t{loadcases_array[i].weights_df.loc['Freeboard']}\t{loadcases_array[i].weights_df.loc['Drag']}\t"
            f"{loadcases_array[i].weights_df.loc['Stability']}\t{loadcases_array[i].weights_df.loc['LeakAngle']}\t"
            f"{loadcases_array[i].weights_df.loc['SecondMoment']}\t{loadcases_array[i].weights_df.loc['WaterplaneCentroid']}\t"
            f"{loadcases_array[i].weights_df.loc['PaddlerCentre']}\t{loadcases_array[i].back_weights_df.loc['Drag']}\n\n"                         
        )

        return 0


class Loadcase: # Albert Xu
    """
    This class will serve as a strcuture to hold loadcase data (including paddler parameters and weights).
    """
    def __init__(self,paddlers_df=pd.DataFrame(), weights_df=pd.DataFrame(), back_weights_df=pd.DataFrame()):
       """Initialize loadcase parameters."""
       self.paddlers_df = paddlers_df # e.g. {"paddler1": {"weight": 70, "seating_position": 2.5}, ...}
       self.weights_df = weights_df # e.g. {"Cp,0.6,0.1,0, "Freeboard": {"mean": 0.15, "stdev": 0.05, "weight": 0}, "Drag": ...}
       self.weights_df["Actual Value"] = 0.0  # Initialize Actual Value column

       self.back_weights_df = back_weights_df
       self.back_weights_df["Actual Value"] = 0.0  # Initialize Actual Value column for reverse canoeing

       # not sure if these are needed yet but we shall find out
       self.waterline = 0.0
       self.init_stability = 0.0
       self.tipping_angle = 0.0
       self.friction_5 = 0.0
       self.cp = 0.0
       self.cm = 0.0
       # Read in the CSV file and convert to dictionary form
       #paddler_df.loc[1] gives you the row
       #paddler_df.loc[1, "height (cm)"] gives the height of paddler 1
    def vertCenterMass(self):
        # Vectorized calculation
        heights = self.paddlers_df["height (cm)"].values
        genders = self.paddlers_df["gender (M/F)"].str.lower().values
        
        # Vectorized conditional calculation
        cVm = np.where(genders == 'f', 0.233 * heights, 0.25 * heights)
        return cVm.tolist()