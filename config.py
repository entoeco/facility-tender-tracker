"""Keyword configuration for matching tenders/opportunities to Sussex technical facilities."""

# Facility name -> list of keywords/phrases (case-insensitive substring match) that
# indicate a tender/opportunity could use that facility.
FACILITY_KEYWORDS = {
    "MRI (3 Tesla)": [
        "mri", "magnetic resonance imaging", "3 tesla", "3t scanner", "3t mri",
    ],
    "X-ray Crystallography": [
        "x-ray crystallography", "xray crystallography", "crystallography",
        "x-ray diffraction", "xrd", "protein crystallography",
    ],
    "NMR": [
        "nmr", "nuclear magnetic resonance",
    ],
    "Mass Spectrometry": [
        "mass spectrometry", "mass spectrometer", "lc-ms", "gc-ms", "ms/ms",
        "proteomics", "metabolomics",
    ],
    "Cryo-Electron Microscopy": [
        "cryo-em", "cryo em", "cryo-electron microscopy", "cryoem",
        "electron microscopy", "electron microscope", "tem imaging",
        "cryogenic electron microscopy",
    ],
    "Web App Development": [
        "web application development", "web app development", "web development",
        "software development services", "full stack development",
        "frontend development", "backend development", "digital platform development",
    ],
    "Mechanical Workshop / Metal 3D Printing": [
        "mechanical workshop", "metal 3d printing", "additive manufacturing",
        "cnc machining", "prototyping services", "metal printing",
        "selective laser melting", "direct metal laser sintering", "dmls",
        "rapid prototyping", "precision engineering workshop",
    ],
    "Biomedical Support / Space": [
        "biomedical research support", "biomedical facility", "laboratory space",
        "research space", "wet lab", "wet lab space", "biomedical services",
    ],
    "Lab Media Prep / Tissue Culture": [
        "media preparation", "tissue culture", "cell culture", "cell culture services",
        "sterile media preparation", "cell line maintenance",
    ],
    "Animal House / In Vivo": [
        "animal house", "animal facility", "in vivo", "vivarium",
        "preclinical animal", "animal husbandry", "laboratory animal",
    ],
    "Confocal / Light Microscopy": [
        "confocal microscopy", "confocal imaging", "light microscopy",
        "fluorescence microscopy", "live cell imaging", "microscopy services",
        "super-resolution microscopy",
    ],
    "MiSeq / Sequencing": [
        "mi-seq", "miseq", "next generation sequencing", "ngs sequencing",
        "dna sequencing", "genome sequencing", "illumina sequencing",
        "sequencing services",
    ],
}

# Broader sector/domain terms that suggest an opportunity is in a relevant research
# or technical field, even if it doesn't name a specific facility/technique.
SECTOR_KEYWORDS = {
    "Structural Biology": [
        "structural biology", "protein structure", "macromolecular structure",
    ],
    "Chemical Analysis": [
        "chemical analysis", "analytical chemistry", "compound analysis",
        "chemical characterisation", "chemical characterization",
    ],
    "Biochemistry": [
        "biochemistry", "biochemical analysis", "biomolecular",
    ],
    "Engineering": [
        "engineering services", "mechanical engineering", "materials engineering",
        "structural engineering", "engineering consultancy", "engineering testing",
    ],
    "Aerospace": [
        "aerospace", "aviation", "aircraft component", "satellite systems",
        "satellite technology", "space sector",
    ],
    "Automotive": [
        "automotive", "vehicle testing", "vehicle component", "motorsport",
    ],
    "Pharma / Biotech": [
        "pharmaceutical", "biotech", "biotechnology", "drug discovery",
        "preclinical research", "clinical trial supplies",
    ],
    "Materials Science": [
        "materials science", "materials characterisation", "materials characterization",
        "nanomaterials", "polymer analysis",
    ],
    "Diagnostics / Medical Devices": [
        "medical device", "diagnostics", "in vitro diagnostics",
        "point of care testing",
    ],
    "Environmental / Life Sciences": [
        "life sciences", "environmental analysis", "genomics", "proteomics",
        "metabolomics research",
    ],
}

# Combined lookup used by the scorer.
ALL_KEYWORDS = {**FACILITY_KEYWORDS, **SECTOR_KEYWORDS}

# Minimum score (number of distinct matched tags) for an opportunity to be stored
# by default in the shortlist view.
DEFAULT_MIN_SCORE = 1
