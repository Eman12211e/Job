"""Dynamic resume bullet generator.

Uses string templates with {PLACEHOLDERS} that get filled based on
the user's selected industry, background, and the specific skill.
Produces ATS-optimized bullet points packed with real keywords.
"""

import random
from typing import Dict, List

# ── Templates by skill category ───────────────────────────────────────
# Each template has slots: {SKILL}, {CONTEXT}, {METRIC}, {DETAIL}

TEMPLATES = {
    "cad": [
        "Designed {CONTEXT} using {SKILL}, reducing design iteration time by {METRIC}.",
        "Created detailed 3D models and assemblies of {CONTEXT} in {SKILL} with full GD&T documentation per ASME Y14.5.",
        "Led CAD modeling of {CONTEXT} in {SKILL}, delivering production-ready drawings {METRIC} ahead of schedule.",
        "Developed parametric models of {CONTEXT} in {SKILL}, enabling rapid design-of-experiments that cut prototyping costs by {METRIC}.",
    ],
    "analysis": [
        "Performed {SKILL} on {CONTEXT}, identifying critical stress concentrations and achieving a {METRIC} weight reduction.",
        "Conducted {SKILL} simulations to validate {CONTEXT}, meeting all load requirements with a factor of safety above {METRIC}.",
        "Executed {SKILL} studies on {CONTEXT}, correlating simulation results within {METRIC} of physical test data.",
        "Applied {SKILL} to optimize {CONTEXT}, reducing peak thermal loads by {METRIC} while maintaining structural integrity.",
    ],
    "controls": [
        "Programmed and commissioned {SKILL} to automate {CONTEXT}, increasing line throughput by {METRIC}.",
        "Developed {SKILL} logic for {CONTEXT}, reducing operator intervention by {METRIC} and improving cycle consistency.",
        "Integrated {SKILL} with {CONTEXT}, achieving {METRIC} uptime improvement through real-time diagnostics.",
    ],
    "manufacturing": [
        "Optimized {CONTEXT} process using {SKILL} principles, reducing scrap rate by {METRIC}.",
        "Implemented {SKILL} techniques for {CONTEXT}, cutting cycle time by {METRIC} across 3 production lines.",
        "Designed tooling and fixtures for {CONTEXT} leveraging {SKILL} knowledge, improving first-pass yield by {METRIC}.",
    ],
    "standards": [
        "Applied {SKILL} standards to {CONTEXT}, ensuring full compliance and passing all audit criteria with zero findings.",
        "Documented {CONTEXT} per {SKILL} requirements, reducing engineering change orders by {METRIC}.",
    ],
    "quality": [
        "Led {SKILL} initiatives on {CONTEXT}, identifying root causes and reducing defect rate by {METRIC}.",
        "Implemented {SKILL} methodology for {CONTEXT}, saving ${METRIC} annually through waste elimination.",
        "Conducted {SKILL} on {CONTEXT}, driving corrective actions that improved process capability (Cpk) by {METRIC}.",
    ],
    "programming": [
        "Developed {SKILL} scripts to automate {CONTEXT}, reducing manual processing time by {METRIC}.",
        "Built {CONTEXT} analysis pipeline in {SKILL}, enabling data-driven decisions that improved {METRIC}.",
        "Created {SKILL}-based tool for {CONTEXT}, processing {METRIC} data points and generating automated reports.",
    ],
    "certifications": [
        "Earned {SKILL} certification, demonstrating proficiency in {CONTEXT} and applied engineering fundamentals.",
        "Leveraged {SKILL} credential to lead {CONTEXT} initiatives, delivering measurable improvements of {METRIC}.",
    ],
    "soft_skills": [
        "Managed {CONTEXT} using {SKILL} methodology, delivering all milestones on time across {METRIC} cross-functional teams.",
        "Produced {SKILL} for {CONTEXT}, enabling clear stakeholder communication and reducing review cycles by {METRIC}.",
    ],
}

# ── Context phrases by industry + category ────────────────────────────

CONTEXTS = {
    "EV/Automotive": {
        "cad": [
            "battery enclosure assembly",
            "EV drivetrain housing",
            "thermal management cold plate",
            "high-voltage junction box",
            "suspension knuckle",
            "motor stator lamination stack",
        ],
        "analysis": [
            "battery pack crash load case",
            "motor thermal runaway scenario",
            "suspension linkage fatigue",
            "EV chassis torsional stiffness",
            "inverter heat sink thermal profile",
        ],
        "controls": [
            "Battery Management System (BMS) firmware",
            "CAN bus vehicle diagnostics",
            "regenerative braking control strategy",
            "EV charging protocol handler",
        ],
        "manufacturing": [
            "battery module assembly line",
            "EV motor lamination stamping",
            "high-voltage harness routing",
            "adhesive bonding for battery enclosures",
        ],
        "standards": [
            "EV battery enclosure per IATF 16949",
            "high-voltage connector specifications",
            "GD&T callouts for drivetrain components",
        ],
        "quality": [
            "battery cell incoming inspection",
            "weld quality on battery trays",
            "EV powertrain DFMEA review",
        ],
        "programming": [
            "test data post-processing for dyno runs",
            "BMS log parsing and anomaly detection",
            "vehicle telemetry dashboards",
        ],
        "certifications": [
            "CAD design and analysis workflows",
            "automotive quality and design processes",
        ],
        "soft_skills": [
            "cross-functional EV platform development",
            "design review documentation packages",
        ],
    },
    "Factory Automation": {
        "cad": [
            "robotic end-effector gripper assembly",
            "conveyor system frame layout",
            "safety guarding enclosure",
            "custom fixture for CNC workholding",
            "pneumatic actuator mounting bracket",
        ],
        "analysis": [
            "pick-and-place cycle structural loads",
            "conveyor drive shaft fatigue",
            "vibration on linear actuator mount",
            "press frame deflection under load",
        ],
        "controls": [
            "PLC-controlled palletizing cell",
            "FANUC robot pick-and-place sequence",
            "Allen-Bradley safety PLC integration",
            "predictive maintenance sensor network",
        ],
        "manufacturing": [
            "CNC turning and milling operations",
            "sheet metal fabrication for enclosures",
            "injection molding tool changeover",
            "automated packaging line",
        ],
        "standards": [
            "production floor ISO 9001 compliance",
            "GD&T specifications for machined parts",
            "machine safety per OSHA and ANSI standards",
        ],
        "quality": [
            "incoming raw material inspection process",
            "SPC implementation on critical dimensions",
            "assembly line defect reduction",
        ],
        "programming": [
            "production database queries and reporting",
            "vibration sensor data pipeline",
            "automated OEE dashboards",
        ],
        "certifications": [
            "manufacturing process optimization",
            "quality management and lean practices",
        ],
        "soft_skills": [
            "factory expansion capital project",
            "standard operating procedure documentation",
        ],
    },
    "Aerospace/Robotics": {
        "cad": [
            "UAV airframe composite structure",
            "satellite bracket assembly",
            "robotic arm joint housing",
            "rocket engine turbopump manifold",
            "landing gear strut assembly",
        ],
        "analysis": [
            "wing spar fatigue load spectrum",
            "spacecraft thermal cycling environment",
            "launch vehicle vibration qualification",
            "propulsion system thermal envelope",
            "robotic gripper contact stress",
        ],
        "controls": [
            "flight control actuator system",
            "robotic arm inverse-kinematics controller",
            "UAV autopilot integration",
            "reaction wheel attitude control",
        ],
        "manufacturing": [
            "composite layup for UAV skins",
            "CNC machining of titanium fittings",
            "additive-manufactured rocket nozzle",
            "robotic arm joint bearing assembly",
        ],
        "standards": [
            "structures per AS9100 Rev D",
            "spacecraft component GD&T callouts",
            "flight hardware configuration management",
        ],
        "quality": [
            "non-conformance review board process",
            "first-article inspection of machined parts",
            "DFMEA on flight-critical mechanisms",
        ],
        "programming": [
            "FEA post-processing automation",
            "telemetry data analysis pipeline",
            "robot path-planning algorithms in ROS",
        ],
        "certifications": [
            "structural analysis and design validation",
            "aerospace engineering fundamentals",
        ],
        "soft_skills": [
            "multi-site satellite development program",
            "test campaign technical reports",
        ],
    },
}

# ── Metrics by category ───────────────────────────────────────────────

METRICS = {
    "cad": ["30%", "25%", "40%", "2 weeks", "15%", "20%"],
    "analysis": [
        "15% weight reduction",
        "2.0",
        "5% of test data",
        "18%",
        "12%",
        "factor of safety of 2.5",
    ],
    "controls": ["22%", "35%", "98.5%", "40%", "15%"],
    "manufacturing": ["30%", "18%", "25%", "12%", "20%"],
    "standards": ["45%", "30%", "20%"],
    "quality": ["60%", "$150K", "0.35", "40%", "$200K"],
    "programming": ["85%", "10,000+", "yield by 8%", "4 hours to 10 minutes"],
    "certifications": ["15%", "cross-functional quality initiatives"],
    "soft_skills": ["4", "3", "50%", "5"],
}

# ── Background adjustments ────────────────────────────────────────────

_STUDENT_PREFIXES = [
    "In senior capstone project, ",
    "During undergraduate research, ",
    "As part of coursework project, ",
    "In student design competition, ",
]

_GRAD_PREFIXES = [
    "As a new graduate engineer, ",
    "In first engineering role, ",
    "",  # Sometimes no prefix
]


def generate_bullets(
    skills: List[str],
    industry: str,
    background: str,
    skills_metadata: List[Dict],
    num_bullets: int = 2,
) -> List[Dict]:
    """Generate ATS-optimized resume bullets for selected skills.

    For each skill, picks a template based on category, fills in
    industry-specific context and realistic metrics.

    Returns: [{"skill": "FEA", "bullets": ["Performed FEA on...", ...]}]
    """
    # Build a lookup: canonical -> category
    cat_map = {s["canonical"]: s["category"] for s in skills_metadata}

    results = []
    for skill in skills:
        category = cat_map.get(skill, "programming")
        templates = TEMPLATES.get(category, TEMPLATES["programming"])
        contexts = CONTEXTS.get(industry, {}).get(category, ["engineering components"])
        metrics = METRICS.get(category, ["20%"])

        bullets = []
        used_templates = set()
        for _ in range(min(num_bullets, len(templates))):
            # Pick a template we haven't used yet for this skill
            available = [t for i, t in enumerate(templates) if i not in used_templates]
            if not available:
                break
            template = random.choice(available)
            used_templates.add(templates.index(template))

            context = random.choice(contexts)
            metric = random.choice(metrics)

            bullet = template.format(
                SKILL=skill,
                CONTEXT=context,
                METRIC=metric,
                DETAIL="full dimensional",
            )

            # Adjust framing for student / recent grad backgrounds
            bullet = _adjust_for_background(bullet, background)
            bullets.append(bullet)

        results.append({"skill": skill, "bullets": bullets})

    return results


def _adjust_for_background(bullet: str, background: str) -> str:
    """Prepend context framing for student vs. professional background."""
    if background == "Current ME Student":
        prefix = random.choice(_STUDENT_PREFIXES)
        # Lowercase the first char of bullet when prepending
        bullet = prefix + bullet[0].lower() + bullet[1:]
    elif background == "Recent ME Graduate":
        prefix = random.choice(_GRAD_PREFIXES)
        if prefix:
            bullet = prefix + bullet[0].lower() + bullet[1:]
    # Experienced Engineer and Career Changer keep professional framing
    return bullet
