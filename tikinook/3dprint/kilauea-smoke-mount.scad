// Kilauea Cove
// (c) 2016 Mark Boszko
// Mount for Seuthe smoke generator inside volcano
// v04

// Compatibility:
// - Seuthe #5 smoke generator (for model trains / buildings, 4.5-6V, 260mA)
// - Trader Sam's Enchanted Tiki Bar - Krakatoa mug

// Concept:
// Mount to hold the smoke generator upright in the base of the tiki mug,
// with a separate ring-light mount and smoke collection cone that will(?)
// make the amount of smoke look larger by creating a cylinder of smoke.

// TODO:
// - Add a ring at the top that I can mount the NeoPixels LED ring to directly

// Resolution
// REZ: $fn fragments per circle
//     default: 0 (draft); export: 100 or more
REZ = 180;

// Smoke generator dimensions
gen_diameter = 10.0;  // in mm
gen_height = 45.0;

gen_distance = 50.0;  // distance from base to holder ring
gen_distance_2 = 35.0;
base_diameter = 50.0;

thickness = 3.0;
stems_count = 3;

hat_distance = gen_height + gen_distance + thickness;  // distance from base to smoke collection hat
hat_diameter = 30.0;  // in mm
hat_slope = 2.0;      // ratio of radius to height, x:1


module base() {
    
    base_inner_diameter = base_diameter - thickness * 2;
    
    // the ring itself
    translate([0, 0, - thickness / 2]) difference() {
        cylinder($fn = REZ, h = thickness, d = base_diameter, center = true);
        cylinder($fn = REZ, h = thickness, d = base_inner_diameter, center = true);
    }

}


module gen_ring(height) {
    
    ring_outer_diameter = gen_diameter + thickness * 2;
    
    // the ring itself
    translate([0, 0, height]) difference() {
        cylinder($fn = REZ, h = thickness, d = ring_outer_diameter, center = true);
        cylinder($fn = REZ, h = thickness, d = gen_diameter, center = true);
    }

}


module stem(height) {
    ring_radius = (gen_diameter + thickness * 2) / 2;
    base_radius = (base_diameter - thickness * 2) / 2;
    stem_triangle_base = base_radius - ring_radius;
    stem_triangle_hypotenuse = sqrt(stem_triangle_base * stem_triangle_base + height * height);
    stem_length = stem_triangle_hypotenuse + thickness * 2;
    stem_angle = 90.0 - asin( height / stem_triangle_hypotenuse );
    translate([-base_radius, 0, 0]) rotate([0, stem_angle, 0]) translate([0, 0, -thickness * 1.5]) cylinder($fn = REZ, h = stem_length, d = thickness, center = false);
}

module stems(height) {
    difference() {
        for (i = [1:stems_count]) {
            angle_delta = 360.0 / stems_count;
            angle = i * angle_delta;
            rotate([0, 0, angle]) stem(height);
        }
        // cleanup where the stems stick out of the rings
        translate([0, 0, height + thickness / 2]) cylinder($fn = REZ, h = thickness * 2, d = gen_diameter, center = true);
        translate([0, 0, -thickness * 1.5]) cylinder($fn = REZ, h = thickness * 2, d = base_diameter + thickness, center = true);
    }   
}

// TODO: Convert this into a printed ring to secure the NeoPixel LED ring to
module hat() {
    height = hat_diameter / 2.0 / hat_slope;
    difference() {
        translate([0, 0, hat_distance]) cylinder(h=height, d1=hat_diameter, d2=0, center=true);translate([0, 0, hat_distance - thickness / 3]) cylinder(h=height, d1=hat_diameter, d2=0, center=true);
    }
}

// TODO: modify this for the hat
module hat_stem() {
    hat_radius = (hat_diameter) / 2;
    base_radius = (base_diameter - thickness * 2) / 2;
    stem_triangle_base = base_radius - hat_radius;
    stem_triangle_hypotenuse = sqrt(stem_triangle_base * stem_triangle_base + hat_distance * hat_distance);
    stem_length = stem_triangle_hypotenuse + thickness;
    stem_angle = 90.0 - asin( hat_distance / stem_triangle_hypotenuse );
    translate([-base_radius, 0, 0]) rotate([0, stem_angle, 0]) translate([0, 0, -thickness * 1.5]) cylinder($fn = REZ, h = stem_length, d = thickness, center = false);
}

module hat_stems() {
    difference() {
        for (i = [1:stems_count]) {
            angle_delta = 360.0 / stems_count;
            angle = i * angle_delta;
            rotate([0, 0, angle]) hat_stem();
        }
        // cleanup where the stems stick out of the rings
        translate([0, 0, gen_distance + thickness / 2]) cylinder($fn = REZ, h = thickness * 2, d = gen_diameter, center = true);
        translate([0, 0, -thickness * 1.5]) cylinder($fn = REZ, h = thickness * 2, d = base_diameter + thickness, center = true);
    }
    
}


module assembly() {
    union() {
        base();
        gen_ring(gen_distance);
        stems(gen_distance);
        gen_ring(gen_distance_2);
        stems(gen_distance_2 );
    }
}

assembly();
// removed hat() because it blocks the smoke too much,
//     but keeping the stems, because they're at least handy for picking up
//     the stand from the narrow inside of the mug
hat_stems();