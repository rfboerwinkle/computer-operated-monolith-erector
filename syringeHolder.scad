screw1Height = 35; A = 35;
screw4Height = 45; B = 45;
screwWidth = 42.4; C = 42.4;
screw4Depth = 4.5; D = 4.5;
cylinderDiameter = 25.5; E = 25.5;
nozzleRadius = 10.5; F = 10.5;
chamferHeight = 5; G = 5;
chamferToEnd = 36; H = 36;
screw4Width = 5.4; I = 5.4;
screwDiameter = 3; J = 3;
screwHeadDiameter = 5; K = 5;
screwMinHeight = 9; L = 9;
screwMaxHeight = 15; M = 15;
bumpDepth = 3; N = 3;
bumpDiameter = 9.5; O = 9.5;
bumpHeight = 57; P = 57;
bumpHeight2 = 18; Q = 18;
dist34 = 14.3; R = 14.3; // might be wrong

syringeZ = (E+9)/2 + 2;
sup = 40; // syringe support

difference(){
    // main body object
    union(){
        // base plate
        translate([-J-4, -(A-Q-8), 0])cube([screwWidth+J*2+8, P-Q-16, L+D+3]);
        // syringe holder
        translate([C/2, P-A-8+sup, syringeZ])rotate([90,0,0])cylinder(h=P-Q-16+sup, d=E+9);
    }

    // raised screw hole 4
    translate([C, B-A, 0])cylinder($fn=20, h=D+1, d=I+1);
    // raised screw hole 3
    translate([C-R, B-A, 0])cylinder($fn=20, h=D+1, d=I+1);

    // through screw 4
    translate([C, B-A, 0])cylinder($fn=20, h=L+D+3, d=J+1);
    // through screw 1
    cylinder($fn=20, h=L+D+3, d=J+1);

    // nozzle
    translate([C/2, P/2, syringeZ])rotate([90,0,0])cylinder(h=P, d=F+1);
    // chamfer
    translate([C/2, H-A, syringeZ])rotate([-90,0,0])cylinder(h=G, d1=F+1, d2=E+1);
    // main syringe
    translate([C/2, H-A+G, syringeZ])rotate([-90,0,0])cylinder(h=P, d=E+1);
    
    translate([C/2,P-A-8,syringeZ])rotate([0,-45,0]){
        cube(sup);
        translate([-sup,0,-sup])cube(sup);
    }
}