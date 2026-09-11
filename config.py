"""Keyword configuration for matching tenders/opportunities to Sussex technical facilities."""

# Facility name -> list of keywords/phrases (case-insensitive substring match) that
# indicate a tender/opportunity could use that facility.
FACILITY_KEYWORDS = {
    "MRI (3 Tesla)": [
        "mri", "magnetic resonance imaging", "3 tesla", "3t scanner", "3t mri",
        "3-tesla", "mri scanner", "mri scanning", "brain imaging", "neuroimaging",
        "preclinical mri", "small animal mri",
    ],
    "X-ray Crystallography": [
        "x-ray crystallography", "xray crystallography", "crystallography",
        "x-ray diffraction", "xrd", "protein crystallography",
        "single crystal x-ray", "crystal structure determination",
        "macromolecular crystallography", "beamline access",
        "diffraction data collection", "structure solution",
    ],
    "NMR": [
        "nmr", "nuclear magnetic resonance", "nmr spectroscopy", "nmr spectrometer",
        "solid-state nmr", "high-field nmr", "nmr facility access",
    ],
    "Mass Spectrometry": [
        "mass spectrometry", "mass spectrometer", "lc-ms", "gc-ms", "ms/ms",
        "proteomics", "metabolomics", "mass spec", "maldi-tof", "maldi imaging",
        "orbitrap", "high resolution mass spectrometry", "hrms", "lipidomics",
        "peptide mapping", "imaging mass spectrometry",
    ],
    "Cryo-Electron Microscopy": [
        "cryo-em", "cryo em", "cryo-electron microscopy", "cryoem",
        "electron microscopy", "electron microscope", "tem imaging",
        "cryogenic electron microscopy", "single particle cryo-em",
        "cryo-electron tomography", "vitrification", "grid preparation",
        "cryo-em facility access", "3d reconstruction",
    ],
    "Web App Development": [
        "web application development", "web app development", "web development",
        "software development services", "full stack development",
        "frontend development", "backend development", "digital platform development",
        "website development", "bespoke software development",
        "application development services", "digital service development",
        "web portal development", "api development", "ux/ui design services",
    ],
    "Mechanical Workshop / Metal 3D Printing": [
        "mechanical workshop", "metal 3d printing", "additive manufacturing",
        "cnc machining", "prototyping services", "metal printing",
        "selective laser melting", "direct metal laser sintering", "dmls",
        "rapid prototyping", "precision engineering workshop", "fabrication workshop",
        "metal fabrication", "custom fabrication", "machining services",
        "laser cutting", "sheet metal fabrication", "welding services",
    ],
    "Biomedical Support / Space": [
        "biomedical research support", "biomedical facility", "laboratory space",
        "research space", "wet lab", "wet lab space", "biomedical services",
        "biomedical research facility", "core research facility",
        "laboratory hire", "bench space", "shared research space",
        "bioscience facility",
    ],
    "Lab Media Prep / Tissue Culture": [
        "media preparation", "tissue culture", "cell culture", "cell culture services",
        "sterile media preparation", "cell line maintenance",
        "microbiological media preparation", "cell culture facility",
        "primary cell culture", "organoid culture", "cell line authentication",
        "mycoplasma testing",
    ],
    "Animal House / In Vivo": [
        "animal house", "animal facility", "in vivo", "vivarium",
        "preclinical animal", "animal husbandry", "laboratory animal",
        "home office licensed facility", "biological services unit", "aspa",
        "rodent facility", "transgenic animal",
    ],
    "Confocal / Light Microscopy": [
        "confocal microscopy", "confocal imaging", "light microscopy",
        "fluorescence microscopy", "live cell imaging", "microscopy services",
        "super-resolution microscopy", "imaging facility", "high content imaging",
        "high content screening", "multiphoton microscopy", "image analysis services",
    ],
    "MiSeq / Sequencing": [
        "mi-seq", "miseq", "next generation sequencing", "ngs sequencing",
        "dna sequencing", "genome sequencing", "illumina sequencing",
        "sequencing services", "amplicon sequencing", "16s sequencing",
        "genomic sequencing", "whole genome sequencing", "rna sequencing",
        "rna-seq", "single cell sequencing", "metagenomics", "library preparation",
    ],
}

# Broader sector/domain terms that suggest an opportunity is in a relevant research
# or technical field, even if it doesn't name a specific facility/technique.
SECTOR_KEYWORDS = {
    "Structural Biology": [
        "structural biology", "protein structure", "macromolecular structure",
        "protein-ligand complex", "drug target structure",
    ],
    "Chemical Analysis": [
        "chemical analysis", "analytical chemistry", "compound analysis",
        "chemical characterisation", "chemical characterization",
        "spectroscopic analysis", "sample characterisation", "trace analysis",
    ],
    "Biochemistry": [
        "biochemistry", "biochemical analysis", "biomolecular",
        "protein purification", "protein expression", "recombinant protein production",
    ],
    "Engineering": [
        "engineering services", "mechanical engineering", "materials engineering",
        "structural engineering", "engineering consultancy", "engineering testing",
        "prototype development", "stress testing", "failure analysis",
    ],
    "Aerospace": [
        "aerospace", "aviation", "aircraft component", "satellite systems",
        "satellite technology", "space sector", "uav", "drone testing",
        "propulsion testing", "wind tunnel testing",
    ],
    "Automotive": [
        "automotive", "vehicle testing", "vehicle component", "motorsport",
        "electric vehicle", "battery testing", "powertrain testing",
    ],
    "Pharma / Biotech": [
        "pharmaceutical", "biotech", "biotechnology", "drug discovery",
        "preclinical research", "clinical trial supplies",
        "formulation development", "cell and gene therapy", "assay development",
    ],
    "Materials Science": [
        "materials science", "materials characterisation", "materials characterization",
        "nanomaterials", "polymer analysis", "surface analysis",
        "thin film characterisation", "nanotechnology",
    ],
    "Diagnostics / Medical Devices": [
        "medical device", "in vitro diagnostics", "point of care testing",
        "diagnostic assay", "diagnostic test kit", "biomarker assay",
    ],
    "Environmental / Life Sciences": [
        "life sciences", "environmental analysis", "genomics", "proteomics",
        "metabolomics research", "microbiome analysis", "water quality analysis",
        "environmental sample analysis",
    ],
}

# Combined lookup used by the scorer.
ALL_KEYWORDS = {**FACILITY_KEYWORDS, **SECTOR_KEYWORDS}

# Minimum score (number of distinct matched tags) for an opportunity to be stored
# by default in the shortlist view.
DEFAULT_MIN_SCORE = 1
