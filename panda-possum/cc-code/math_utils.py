
"""
Last modified by Lucas on Jan 25, 2026

Written and tested by Albert, Elorie, Folu, John, Lucas (2T6 Hull & Structural Directors), Elliot, and J

This module contains functions for calculating areas and moments of sections defined by cubic splines.
"""
import math

# Testing Albert

def spline_area(P0y, P0z, P1y, P1z, P2y, P2z, P3y, P3z, ti, tf):
    '''
    original c++ function:
    double SplineArea(double P0y, double P0z, double P1y, double P1z,
						double P2y, double P2z, double P3y, double P3z,
						double ti, double tf) {
        
        double A1 = P0y - 3*P1y + 3*P2y - P3y;
        double B1 = 3*P1y - 6*P2y + 3*P3y;
        double C1 = 3*P2y - 3*P3y;
        double D1 = P3y;

        double A2 = 0;
        double B2 = 3*P0z - 9*P1z + 9*P2z - 3*P3z;
        double C2 = 6*P1z - 12*P2z + 6*P3z;
        double D2 = 3*P2z - 3*P3z;

        double E[7];
        E[6] = A1*A2;
        E[5] = A1*B2 + B1*A2;
        E[4] = A1*C2 + B1*B2 + C1*A2;
        E[3] = A1*D2 + B1*C2 + C1*B2 + D1*A2;
        E[2] = B1*D2 + C1*C2 + D1*B2;
        E[1] = C1*D2 + D1*C2;
        E[0] = D1*D2;

        double area = 0;
        int i;
        for (i = 0; i < 7; i++) {
            area += E[i]/(i+1) * (pow(tf,(i+1)) - pow(ti,(i+1)));
        }
        return area;
    }

    '''
    A1 = P0y - 3*P1y + 3*P2y - P3y
    B1 = 3*P1y - 6*P2y + 3*P3y
    C1 = 3*P2y - 3*P3y
    D1 = P3y

    A2 = 0
    B2 = 3*P0z - 9*P1z + 9*P2z - 3*P3z
    C2 = 6*P1z - 12*P2z + 6*P3z
    D2 = 3*P2z - 3*P3z

    E = [0]*7
    E[6] = A1*A2
    E[5] = A1*B2 + B1*A2
    E[4] = A1*C2 + B1*B2 + C1*A2
    E[3] = A1*D2 + B1*C2 + C1*B2 + D1*A2
    E[2] = B1*D2 + C1*C2 + D1*B2
    E[1] = C1*D2 + D1*C2
    E[0] = D1*D2

    area = 0
    for i in range(7):
        area += E[i]/(i+1) * (tf**(i+1) - ti**(i+1))
    return area


def spline_moment(P0y, P0z, P1y, P1z, P2y, P2z, P3y, P3z, ti, tf):
    '''
    original c++ function:
    int SplineMoment(double P0y, double P0z, double P1y, double P1z,
							 double P2y, double P2z, double P3y, double P3z,
							 double ti, double tf, double& momentareay, double& momentareaz) {

        double A1 = P0y - 3*P1y + 3*P2y - P3y;
        double B1 = 3*P1y - 6*P2y + 3*P3y;
        double C1 = 3*P2y - 3*P3y;
        double D1 = P3y;

        double A2 = 0;
        double B2 = 3*P0z - 9*P1z + 9*P2z - 3*P3z;
        double C2 = 6*P1z - 12*P2z + 6*P3z;
        double D2 = 3*P2z - 3*P3z;

        double A3 = P0z - 3*P1z + 3*P2z - P3z;
        double B3 = 3*P1z - 6*P2z + 3*P3z;
        double C3 = 3*P2z - 3*P3z;
        double D3 = P3z;

        double A4 = 0;
        double B4 = 3*P0y - 9*P1y + 9*P2y - 3*P3y;
        double C4 = 6*P1y - 12*P2y + 6*P3y;
        double D4 = 3*P2y - 3*P3y;

        double E[7];
        E[6] = A1*A2;
        E[5] = A1*B2 + B1*A2;
        E[4] = A1*C2 + B1*B2 + C1*A2;
        E[3] = A1*D2 + B1*C2 + C1*B2 + D1*A2;
        E[2] = B1*D2 + C1*C2 + D1*B2;
        E[1] = C1*D2 + D1*C2;
        E[0] = D1*D2;

        double L[10];
        L[9] = A3*E[6];
        L[8] = B3*E[6] + A3*E[5];
        L[7] = C3*E[6] + B3*E[5] + A3*E[4];
        L[6] = D3*E[6] + C3*E[5] + B3*E[4] + A3*E[3];
        L[5] = D3*E[5] + C3*E[4] + B3*E[3] + A3*E[2];
        L[4] = D3*E[4] + C3*E[3] + B3*E[2] + A3*E[1];
        L[3] = D3*E[3] + C3*E[2] + B3*E[1] + A3*E[0];
        L[2] = D3*E[2] + C3*E[1] + B3*E[0];
        L[1] = D3*E[1] + C3*E[0];
        L[0] = D3*E[0];

        double Ey[7];
        Ey[6] = A3*A4;
        Ey[5] = A3*B4 + B3*A4;
        Ey[4] = A3*C4 + B3*B4 + C3*A4;
        Ey[3] = A3*D4 + B3*C4 + C3*B4 + D3*A4;
        Ey[2] = B3*D4 + C3*C4 + D3*B4;
        Ey[1] = C3*D4 + D3*C4;
        Ey[0] = D3*D4;

        double Ly[10];
        Ly[9] = A1*Ey[6];
        Ly[8] = B1*Ey[6] + A1*Ey[5];
        Ly[7] = C1*Ey[6] + B1*Ey[5] + A1*Ey[4];
        Ly[6] = D1*Ey[6] + C1*Ey[5] + B1*Ey[4] + A1*Ey[3];
        Ly[5] = D1*Ey[5] + C1*Ey[4] + B1*Ey[3] + A1*Ey[2];
        Ly[4] = D1*Ey[4] + C1*Ey[3] + B1*Ey[2] + A1*Ey[1];
        Ly[3] = D1*Ey[3] + C1*Ey[2] + B1*Ey[1] + A1*Ey[0];
        Ly[2] = D1*Ey[2] + C1*Ey[1] + B1*Ey[0];
        Ly[1] = D1*Ey[1] + C1*Ey[0];
        Ly[0] = D1*Ey[0];

        momentareaz = 0;
        momentareay = 0;
        int i;
        for (i = 0; i < 10; i++) {
            momentareaz +=  L[i]/(i+1) * (pow(tf,(i+1)) - pow(ti,(i+1)));
            momentareay += Ly[i]/(i+1) * (pow(tf,(i+1)) - pow(ti,(i+1)));
        }

        double Piy = Spline(A1,B1,C1,D1,ti);
        double Piz = Spline(A3,B3,C3,D3,ti);
        double Pfy = Spline(A1,B1,C1,D1,tf);
        double Pfz = Spline(A3,B3,C3,D3,tf);

        momentareay += Piy*Piy*Piz/2 - Pfy*Pfy*Pfz/2;	// extra rectangular regions

        momentareaz = momentareaz;		// I think the negatives should be here...
        momentareay = -momentareay;			// But not here?

        return 0;
    }

    '''
    A1 = P0y - 3*P1y + 3*P2y - P3y
    B1 = 3*P1y - 6*P2y + 3*P3y
    C1 = 3*P2y - 3*P3y
    D1 = P3y

    A2 = 0
    B2 = 3*P0z - 9*P1z + 9*P2z - 3*P3z
    C2 = 6*P1z - 12*P2z + 6*P3z
    D2 = 3*P2z - 3*P3z

    A3 = P0z - 3*P1z + 3*P2z - P3z
    B3 = 3*P1z - 6*P2z + 3*P3z
    C3 = 3*P2z - 3*P3z
    D3 = P3z

    A4 = 0
    B4 = 3*P0y - 9*P1y + 9*P2y - 3*P3y
    C4 = 6*P1y - 12*P2y + 6*P3y
    D4 = 3*P2y - 3*P3y

    E = [0]*7
    E[6] = A1*A2
    E[5] = A1*B2 + B1*A2
    E[4] = A1*C2 + B1*B2 + C1*A2
    E[3] = A1*D2 + B1*C2 + C1*B2 + D1*A2
    E[2] = B1*D2 + C1*C2 + D1*B2
    E[1] = C1*D2 + D1*C2
    E[0] = D1*D2

    L = [0]*10
    L[9] = A3*E[6]
    L[8] = B3*E[6] + A3*E[5]
    L[7] = C3*E[6] + B3*E[5] + A3*E[4]
    L[6] = D3*E[6] + C3*E[5] + B3*E[4] + A3*E[3]
    L[5] = D3*E[5] + C3*E[4] + B3*E[3] + A3*E[2]
    L[4] = D3*E[4] + C3*E[3] + B3*E[2] + A3*E[1]
    L[3] = D3*E[3] + C3*E[2] + B3*E[1] + A3*E[0]
    L[2] = D3*E[2] + C3*E[1] + B3*E[0]
    L[1] = D3*E[1] + C3*E[0]
    L[0] = D3*E[0]

    Ey = [0]*7
    Ey[6] = A3*A4
    Ey[5] = A3*B4 + B3*A4
    Ey[4] = A3*C4 + B3*B4 + C3*A4
    Ey[3] = A3*D4 + B3*C4 + C3*B4 + D3*A4
    Ey[2] = B3*D4 + C3*C4 + D3*B4
    Ey[1] = C3*D4 + D3*C4
    Ey[0] = D3*D4

    Ly = [0]*10
    Ly[9] = A1*Ey[6]
    Ly[8] = B1*Ey[6] + A1*Ey[5]
    Ly[7] = C1*Ey[6] + B1*Ey[5] + A1*Ey[4]
    Ly[6] = D1*Ey[6] + C1*Ey[5] + B1*Ey[4] + A1*Ey[3]
    Ly[5] = D1*Ey[5] + C1*Ey[4] + B1*Ey[3] + A1*Ey[2]
    Ly[4] = D1*Ey[4] + C1*Ey[3] + B1*Ey[2] + A1*Ey[1]
    Ly[3] = D1*Ey[3] + C1*Ey[2] + B1*Ey[1] + A1*Ey[0]
    Ly[2] = D1*Ey[2] + C1*Ey[1] + B1*Ey[0]
    Ly[1] = D1*Ey[1] + C1*Ey[0]
    Ly[0] = D1*Ey[0]

    moment_area_z = 0
    moment_area_y = 0

    for i in range(10):
        moment_area_z += L[i]/(i+1) * ((tf**(i+1)) - (ti**(i+1)))
        moment_area_y += Ly[i]/(i+1) * ((tf**(i+1)) - (ti**(i+1)))

    Piy = spline(A1,B1,C1,D1,ti)
    Piz = spline(A3,B3,C3,D3,ti)
    Pfy = spline(A1,B1,C1,D1,tf)
    Pfz = spline(A3,B3,C3,D3,tf)

    moment_area_y += Piy*Piy*Piz/2 - Pfy*Pfy*Pfz/2	#extra rectangular regions

    moment_area_z = moment_area_z		# I think the negatives should be here...
    moment_area_y = -moment_area_y			# But not here?

    return moment_area_y, moment_area_z
    # TODO: complete this function
    


def solver_cubic(a, b, c, d):
    '''
    original c++ function:

    double SolveCubic(double a, double b, double c, double d) {
    /* Only works if there's 1 real root
        double q,r,s,t;
        
        q = (9*a*b*c - 27*a*a*d - 2*b*b*b)/(54*a*a*a);
        r = sqrt(pow(((3*a*c - b*b)/(9*a*a)),3) + q*q);
        s = pow((q+r),1./3.);
        if (q>r)
            t = pow((q-r),1./3.);
        else
            t = -pow((r-q),1./3.);

        return (s + t - b/(3.*a));
    */

        double ap,bp,cp,p,q,f;
        double rootfr,rootfi,gr,gi,magg,argg,magu1,argu1,u1r,u1i,u2r,u2i,u3r,u3i,x1r,x1i,x2r,x2i,x3r,x3i;

        ap = b/a;
        bp = c/a;
        cp = d/a;

        p = bp - ap*ap/3.;
        q = cp + (2*ap*ap*ap - 9*ap*bp)/27.;

        if (p == 0 && q == 0)
            return -ap/3.;
        if (p == 0) {
            magg = q;
            argg = 0;
        }
        else {
            f = q*q/4. + p*p*p/27.;
            if (f < 0) {
                rootfr = 0;
                rootfi = sqrt(-f);
            }
            else {
                rootfr = sqrt(f);
                rootfi = 0;
            }

            gr = rootfr + q/2.;
            gi = rootfi;

            magg = sqrt(gr*gr+gi*gi);
            argg = atan2(gi,gr) + (rootfi < 0 ? 2*PI : 0);
        }

        magu1 = pow(magg,1./3.);
        argu1 = argg/3.;

        u1r = magu1*cos(argu1);
        u1i = magu1*sin(argu1);

        u2r = -0.5*u1r - sqrt(3)/2.*u1i;
        u2i = -0.5*u1i + sqrt(3)/2.*u1r;

        u3r = -0.5*u1r + sqrt(3)/2.*u1i;
        u3i = -0.5*u1i - sqrt(3)/2.*u1r;

        x1r = p/3.*u1r/(u1r*u1r+u1i*u1i) - u1r - ap/3.;
        x1i = -p/3.*u1i/(u1r*u1r+u1i*u1i) - u1i;

        x2r = p/3.*u2r/(u2r*u2r+u2i*u2i) - u2r - ap/3.;
        x2i = -p/3.*u2i/(u2r*u2r+u2i*u2i) - u2i;

        x3r = p/3.*u3r/(u3r*u3r+u3i*u3i) - u3r - ap/3.;
        x3i = -p/3.*u3i/(u3r*u3r+u3i*u3i) - u3i;
        
        // determine which real root falls between 0 and 1 - if none do, return -1
        double threshold = 1e-10;		// zero threshold
        double ROUNDOFF = threshold*1000;	// this one is killing me
        if (x1r <= 1+ROUNDOFF && x1r >= 0-ROUNDOFF && fabs(x1i)<threshold)
            return x1r;
        else if (x2r <= 1+ROUNDOFF && x2r >= 0-ROUNDOFF && fabs(x2i)<threshold)
            return x2r;
        else if (x3r <= 1+ROUNDOFF && x3r >= 0-ROUNDOFF && fabs(x3i)<threshold)
            return x3r;

        return -1;

    }
    '''
    if a == 0:
        print(f"WARNING: solver_cubic called with a=0, coefficients: {a}, {b}, {c}, {d}")

    ap = b / a
    bp = c / a
    cp = d / a

    p = bp - ap * ap / 3.0
    q = cp + (2 * (ap**3) - 9 * (ap * bp)) / 27.0

    if p == 0.0 and q == 0.0:
       return (-ap / 3.0)

    elif p == 0.0:
        magg = q
        argg = 0.0

    else:
        f = ((q**2) / 4.0) + ((p**3) / 27.0)
        if f < 0.0:
            rootfr = 0.0
            rootfi = math.sqrt(-f)

        else:
            rootfr = math.sqrt(f)
            rootfi = 0.0

        gr = rootfr + (q / 2.0)
        gi = rootfi

        magg = math.sqrt(gr**2 + gi**2)
        argg = math.atan2(gi, gr)
        if rootfi < 0.0:
            argg += 2 * math.pi

    magu1 = math.cbrt(magg)
    argu1 = argg / 3.0

    u1r = magu1 * math.cos(argu1)
    u1i = magu1 * math.sin(argu1)

    u2r = -0.5 * u1r - math.sqrt(3) / 2.0 * u1i
    u2i = -0.5 * u1i + math.sqrt(3) / 2.0 * u1r

    u3r = -0.5 * u1r + math.sqrt(3) / 2.0 * u1i
    u3i = -0.5 * u1i - math.sqrt(3) / 2.0 * u1r

    x1r = p / 3.0 * u1r / (u1r**2 + u1i**2) - u1r - ap / 3.0
    x1i = -p / 3.0 * u1i / (u1r**2 + u1i**2) - u1i

    x2r = p / 3.0 * u2r / (u2r**2 + u2i**2) - u2r - ap / 3.0
    x2i = -p / 3.0 * u2i / (u2r**2 + u2i**2) - u2i
    x3r = p / 3.0 * u3r / (u3r**2 + u3i**2) - u3r - ap / 3.0
    x3i = -p / 3.0 * u3i / (u3r**2 + u3i**2) - u3i

    threshold = 1e-10
    ROUNDOFF = threshold * 1000

    if (x1r <= 1 + ROUNDOFF and x1r >= 0 - ROUNDOFF and math.fabs(x1i) < threshold):
        return x1r
    elif (x2r <= 1 + ROUNDOFF and x2r >= 0 - ROUNDOFF and math.fabs(x2i) < threshold):
        return x2r
    elif (x3r <= 1 + ROUNDOFF and x3r >= 0 - ROUNDOFF and math.fabs(x3i) < threshold):
        return x3r

    return -1

def section_resultant(P0y, P0z, P1y, P1z, P2y, P2z, P3y, P3z, d, theta):
    '''
    original c++ function:
    int SectionResultant(double P0y, double P0z, double P1y, double P1z,
                        double P2y, double P2z, double P3y, double P3z,
                        double d, double theta,												// d is freeboard
                        double& magnitude, double& yloc, double& zloc) {
    
        if (d > -P3z) {
            magnitude = 0;
            yloc = 0;
            zloc = 0;
            return 0;

        int flag = 0;

        double A1 = P0y - 3*P1y + 3*P2y - P3y;
        double B1 = 3*P1y - 6*P2y + 3*P3y;
        double C1 = 3*P2y - 3*P3y;
        double D1 = P3y;

        double A3 = P0z - 3*P1z + 3*P2z - P3z;
        double B3 = 3*P1z - 6*P2z + 3*P3z;
        double C3 = 3*P2z - 3*P3z;
        double D3 = P3z;

        double ti, tfr, tfl;
        if (d == 0 && theta == 0) {
            ti = 0;
            tfr = 1;
            tfl = 1;
        } else {
            ti = 0;								// lower bound
            tfr = SolveCubic(A3-tan(theta)*A1, B3-tan(theta)*B1, C3-tan(theta)*C1, D3-tan(theta)*D1+d-P0z);	// upper bound right side
            if (tfr < 0)
                flag = -1;				// leak point
            tfl = SolveCubic(A3+tan(theta)*A1, B3+tan(theta)*B1, C3+tan(theta)*C1, D3+tan(theta)*D1+d-P0z);	// upper bound left side
            if (tfl < 0)
                flag = -1;
        }

        double arearspline = SplineArea(P0y,P0z,P1y,P1z,P2y,P2z,P3y,P3z,ti,tfr);
        double arealspline = SplineArea(P0y,P0z,P1y,P1z,P2y,P2z,P3y,P3z,ti,tfl);

        double momyrspline, momzrspline, momylspline, momzlspline;
        SplineMoment(P0y,P0z,P1y,P1z,P2y,P2z,P3y,P3z,ti,tfr,momyrspline,momzrspline);
        SplineMoment(P0y,P0z,P1y,P1z,P2y,P2z,P3y,P3z,ti,tfl,momylspline,momzlspline);

        momylspline = - momylspline;

        double ytfr = Spline(A1,B1,C1,D1,tfr);
        double ztfr = Spline(A3,B3,C3,D3,tfr);
        double ytfl = -Spline(A1,B1,C1,D1,tfl);
        double ztfl = Spline(A3,B3,C3,D3,tfl);

        double areartri = -ytfr*((P0z-d)-ztfr)/2;
        double arealtri = -ytfl*((P0z-d)-ztfl)/2;

        double arear = arearspline - areartri;		// subtract triangular portion - there's an explicit negative here
        double areal = arealspline + arealtri;		// add triangular portion

        magnitude = arear + areal;

        double ymoment = momyrspline - 1./3.*ytfr*areartri + momylspline + 1./3.*ytfl*arealtri;
        double zmoment = momzrspline - (ztfr - 1./3.*(ztfr - (P0z-d)))*areartri
                            + momzlspline + (P0z-d - 2./3.*((P0z-d) - ztfl))*arealtri;

        yloc = (magnitude == 0 ? 0 : ymoment/magnitude);	
        zloc = (magnitude == 0 ? 0 : zmoment/magnitude);

        if (flag == -1)
            return -1;
        return 0;
    }
    '''
    magnitude = 0
    yloc = 0.0
    zloc = 0.0
    if d > -P3z:
        return 0, magnitude, yloc, zloc

    flag = 0

    A1 = P0y - 3 * P1y + 3 * P2y - P3y
    B1 = 3 * P1y - 6 * P2y + 3 * P3y
    C1 = 3 * P2y - 3 * P3y
    D1 = P3y
    A3 = P0z - 3 * P1z + 3 * P2z - P3z
    B3 = 3 * P1z - 6 * P2z + 3 * P3z
    C3 = 3 * P2z - 3 * P3z
    D3 = P3z

    if d == 0 and theta == 0:
        ti = 0.0
        tfr = 1.0
        tfl = 1.0

    else:
        ti = 0.0
        tfr = solver_cubic(A3 - math.tan(theta)*A1, B3 - math.tan(theta)*B1, C3 - math.tan(theta)*C1, D3 - math.tan(theta)*D1 + d - P0z)
        if tfr < 0:
            # raise ValueError("LEAK - Section Resultant detected leak on right side")
            flag = -1

        tfl = solver_cubic(A3 + math.tan(theta)*A1, B3 + math.tan(theta)*B1, C3 + math.tan(theta)*C1, D3 + math.tan(theta)*D1 + d - P0z)
        if tfl < 0:
            # raise ValueError("LEAK - Section Resultant detected leak on left side")
            flag = -1

    arearspline = spline_area(P0y, P0z, P1y, P1z, P2y, P2z, P3y, P3z, ti, tfr)
    arealspline = spline_area(P0y, P0z, P1y, P1z, P2y, P2z, P3y, P3z, ti, tfl)
    momyrspline, momzrspline = spline_moment(P0y, P0z, P1y, P1z, P2y, P2z, P3y, P3z, ti, tfr)
    momylspline, momzlspline = spline_moment(P0y, P0z, P1y, P1z, P2y, P2z, P3y, P3z, ti, tfl)

    momylspline = -momylspline

    ytfr = spline(A1, B1, C1, D1, tfr)
    ztfr = spline(A3, B3, C3, D3, tfr)
    ytfl = -spline(A1, B1, C1, D1, tfl)
    ztfl = spline(A3, B3, C3, D3, tfl)

    areartri = -ytfr * ((P0z - d) - ztfr) / 2.0
    arealtri = -ytfl * ((P0z - d) - ztfl) / 2.0

    arear = arearspline - areartri
    areal = arealspline + arealtri

    magnitude = arear + areal

    ymoment = (momyrspline - (1.0/3.0)*ytfr*areartri + momylspline + (1.0/3.0)*ytfl*arealtri)

    zmoment = (momzrspline - (ztfr - (1.0/3.0)*(ztfr - (P0z - d)))*areartri + momzlspline + (P0z - d - (2.0/3.0)*((P0z - d) - ztfl))*arealtri)

    if magnitude == 0:
        yloc = 0.0
        zloc = 0.0
    else:
        yloc = ymoment / magnitude
        zloc = zmoment / magnitude

    if flag == -1:
        return -1, magnitude, yloc, zloc

    return 0, magnitude, yloc, zloc

def spline(A, B, C, D, t):
    '''
    original c++ function:
    double Spline(double A, double B, double C, double D, double t) {
	return (A*t*t*t + B*t*t + C*t + D);
    }
    '''
    return (A*t**3 + B*t**2 + C*t + D)

def ramp(x, t):
	return (t/2. * math.log(0.5*math.exp(x/t) + 0.5*math.exp(-x/t)) + x/2. + t*math.log(2.)/2.)

def gaussian(mean, std, x):
    exponential = -1 * ( (x-mean)**2 /(2*std**2) )
    return math.exp(exponential)