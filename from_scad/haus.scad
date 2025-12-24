m=1000/1000;
c=m/100;
thickness=0.4*m;
sidewalllength=10*m; // wall length
frontwalllength=10*m;

module frame (size) { 
  x=size[0];y=size[1];w=size[2];t=size[3];
  // xsize, ysize, width, thickness 
  union() {
    cube([x,w,t]);
    translate ([0,y-w,0]) cube([x,w,t]);
    cube([w,y,t]);
    translate ([x-w,0,0]) cube([w,y,t]);
  }
}
  
       
module window (size) {
  x=size[0];y=size[1];w=size[2];
  fsize=[x+0.2*c,y+0.2*c,5.2*c,w-5*c];
  union () {
    translate([-0.1*c,-0.1*c,0]) frame(fsize);
    translate([5*c,5*c,5*c]) frame([x-10*c,y-10*c,5*c,w-13*c]);
    translate([-0.04*m,-0.05*m,w-0.05*m]) 
      rotate([10,0,0]) cube([x+2*0.04*m,0.06*m,0.1*m]);
  }
}

module windowhole (size) {
  translate ([0,0,-0.05*m]) cube(size+[0,0,0.1*m]);
}

// frame ( [1*m,0.5*m,0.1*m,0.05*m]);
module frontwall () {
wsize=[1.08*m,1*m,thickness];
wpos1=[3.55*m,1.81*m,0];
wpos2=[5.75*m,1.81*m,0];
wpos3=[7.92*m,1.81*m,0];
wpos4=[1.2*m,4.49*m,0];
wpos5=[3.55*m,4.49*m,0];
wpos6=[5.75*m,4.49*m,0];
wpos7=[7.92*m,4.49*m,0];
union() {
  difference() {
    cube([frontwalllength,6.08*m,thickness]);
    //translate([-1.9*thickness,-1*c,0]) rotate([0,45,0]) cube([2*thickness,7*m,2*thickness]);
    //translate([10*m-0.9*thickness,-1*c,0]) rotate([0,45,0]) cube([2*thickness,7*m,2*thickness]);
    translate([-1*c,-1*c,-0.05*m]) cube([2.36*m,2.87*m,thickness+10*c]);
    translate(wpos1) windowhole(wsize);
    translate(wpos2) windowhole(wsize);
    translate(wpos3) windowhole(wsize);
    translate(wpos4) windowhole(wsize);
    translate(wpos5) windowhole(wsize);
    translate(wpos6) windowhole(wsize);
    translate(wpos7) windowhole(wsize);
  }
  translate(wpos1) window(wsize);
  translate(wpos2) window(wsize);
  translate(wpos3) window(wsize);
  translate(wpos4) window(wsize);
  translate(wpos5) window(wsize);
  translate(wpos6) window(wsize);
  translate(wpos7) window(wsize);
}
}

module sidewall () {
  wl = sidewalllength;
  linear_extrude (height=thickness) 
    polygon(points=[[0,0],[10*m,0],
		    [10*m,3.3*m],[wl-2.07*m,3.3*m],[wl-2.07*m,6.08*m],
		    [(wl-2.07*m)/2,wl-1*m],[0,6.08*m]]);
  //cube([10*m,6.08*m,thickness]);
}

module backwalllower () {
  wsize=[1.48*m,1.4*m,thickness];
  wpos1=[0.7*m,1.41*m,0];
  wpos2=[0.7*m+1.48*m,1.41*m,0];
  wpos3=[6.3*m,1.41*m,0];
  wpos4=[6.3*m+1.48*m,1.41*m,0];
  dpos=[0.7*m+2*1.48*m,40*c,0];
  dsize=[1.2*m,(1.4+1.01)*m,thickness];
  union () {
    difference() {
      cube([10*m,3.3*m,thickness]);
      translate(wpos1) windowhole(wsize);
      translate(wpos2) windowhole(wsize);
      translate(wpos3) windowhole(wsize);
      translate(wpos4) windowhole(wsize);
      translate(dpos) windowhole(dsize);
    }
    translate(wpos1) window(wsize);
    translate(wpos2) window(wsize);
    translate(wpos3) window(wsize);
    translate(wpos4) window(wsize);
    translate(dpos) window(dsize);
  }
}

module balconyfloor() {
  cube([10*m,2.07*m+thickness,thickness]);
}

module backwallupper () {
  wsize=[2*1.48*m,1.4*m,thickness];
  wpos=[6.5*m,1.41*m,0];
  dpos1=[1.7*m,40*c,0];
  dpos2=[4*m,40*c,0];
  dsize=[1.2*m,(1.4+1.01)*m,thickness];
  union () {
    difference() {
      cube([10*m,(6.08-3.3)*m+thickness,thickness]);
      translate(wpos) windowhole(wsize);
      translate(dpos1) windowhole(dsize);
      translate(dpos2) windowhole(dsize);
    }
    translate(wpos) window(wsize);
    translate(dpos1) window(dsize);
    translate(dpos2) window(dsize);
  }
}

module house_without_roof() {
translate ([0,thickness,0]) rotate ([90,0,0]) frontwall();
translate ([0,0,0]) rotate([90,0,90]) sidewall();
translate ([10*m-thickness,0,0]) rotate([90,0,90]) sidewall();
translate ([10*m,sidewalllength-thickness+1*c,0]) rotate ([90,0,180]) backwalllower();
translate ([0,sidewalllength-2.07*m-thickness,3.3*m-thickness]) balconyfloor();
translate ([10*m,sidewalllength-2.07*m-thickness+1*c,2.9*m]) rotate ([90,0,180]) backwallupper();
// terrase
translate([10*m-5.5*m,sidewalllength-5*c,0]) cube([5.5*m,3*m,0.4*m]); 
// garage
translate([0,3.2*m,0]) rotate([90,0,0]) 
  frame([2.36*m+thickness/2,2.87*m,thickness/2,3.2*m]);
translate([0,3.18*m,0]) rotate([90,0,0]) cube([2.36*m+thickness/2,2.87*m,thickness/2])
// to stabalize the contraction
frame([10*m,sidewalllength,2*thickness,thickness/2]);
translate([0,0,3*m]) 
  frame([10*m,sidewalllength-2.07*m,2*thickness,thickness/2]);
translate([0,0,5.8*m]) 
  frame([10*m,sidewalllength-2.07*m,2*thickness,thickness/2]);
}

module roof() {
  wl = sidewalllength; //-2.07*m 
  sf = 1.2; 
  difference () {
    scale([1,sf,sf]) translate ([0,0,thickness]) rotate([90,0,90]) 
      linear_extrude (height=frontwalllength) 
      polygon(points=[[-15*c,0],[wl-2.07*m+15*c,0*m],[(wl-2.07*m)/2,wl-(1+6.08)*m+15*c]]);
    scale([1,sf,sf]) translate ([-15*c,0,10*c]) rotate([90,0,90]) 
      //	  linear_extrude (height=thickness+30*c) 
      linear_extrude (height=frontwalllength+30*c) 
      polygon(points=[[0,0],[wl-2.07*m,0*m],[(wl-2.07*m)/2,wl-(1+6.08)*m]]);
    /*
      scale([1,sf,sf]) translate ([frontwalllength-15*c-thickness,0,0]) rotate([90,0,90]) 
      linear_extrude (height=thickness+30*c) 
      polygon(points=[[0,0],[wl-2.07*m,0*m],[(wl-2.07*m)/2,wl-(1+6.08)*m]]);
    */
  }
  //translate([2*thickness+15*c,2*thickness+15*c,0]) cube([frontwalllength-4*thickness-30*c,wl-2.07*m-30*c-4*thickness,thickness+5*c]);

  scale([1,sf,sf]) translate ([0,0,0]) rotate([90,0,90]) 
    linear_extrude (height=frontwalllength) 
    //	polygon(points=[[0,0],[0,thickness],[2*thickness,3*thickness-10*c],[-2*thickness,0]]);
    polygon(points=[[0,thickness],[0,thickness],[2*thickness,3*thickness-20*c],[-1.5*thickness,thickness]]);
  scale([1,sf,sf]) translate ([frontwalllength,sidewalllength-2.07*m,0]) rotate([90,0,-90]) 
    linear_extrude (height=frontwalllength) 
    //	polygon(points=[[0,0],[0,thickness],[2*thickness,3*thickness-10*c],[-2*thickness,0]]);
    polygon(points=[[0,thickness],[0,thickness],[2*thickness,3*thickness-20*c],[-1.5*thickness,thickness]]);

  scale([1,sf,sf]) translate([0,wl-(6.08)*m+5*c,(wl-2.07*m-100*c)/2]) rotate ([90,0,90]) 
    linear_extrude (height=frontwalllength) circle(r=thickness/2, $fn=60);
  /*
    for (i=[1:10]) {
    scale([1,sf,sf]) translate ([i*5,0,thickness]) rotate([90,0,90]) 
    linear_extrude (height=0.5) 
    polygon(points=[[-15*c,0],[wl-2.07*m+15*c,0*m],[(wl-2.07*m)/2,wl-(1+6.08)*m+15*c]]);
    }*/
}

/*
module roof () {
    roof1();
}
*/

house_without_roof();
translate([0,-80*c,6.08*m-70*c]) 
//translate([0,0,-50*c]) 
roof();
