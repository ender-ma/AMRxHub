"""Seed the glossary with the terms that were previously hard-coded in main/glossary.html.

Safe to run on a database that already has glossary data: existing categories and
terms (matched by slug) are left untouched. Reversing removes only the seeded rows.
"""
from django.db import migrations

CATEGORIES = [
    # slug, name, icon, description, order
    ("core", "Core Terms", "fas fa-star",
     "The must-have terms everyone should know when talking about AMR.", 1),
    ("technical", "Technical but Important", "fas fa-hospital",
     "Awareness-level terms used in clinical and surveillance settings.", 2),
    ("genetics", "Genetics and Mechanisms", "fas fa-dna",
     "How resistance arises and spreads, for a deeper understanding.", 3),
    ("additional", "Additional Useful Terms", "fas fa-book-open",
     "Further concepts that help explain how resistance develops and is tackled.", 4),
]

TERMS = [
    # slug, term, abbreviation, category slug, definition
    ("amr", "Antimicrobial Resistance", "AMR", "core",
     "When microorganisms (bacteria, viruses, fungi, parasites) evolve and stop responding to medicines that used to kill them."),
    ("antimicrobials", "Antimicrobials", "", "core",
     "Medicines that treat infections, including antibiotics (bacteria), antivirals (viruses), antifungals (fungi), and antiparasitics (parasites)."),
    ("antibiotic-resistance", "Antibiotic Resistance", "", "core",
     "A specific type of AMR where bacteria no longer respond to antibiotics."),
    ("superbugs", "Superbugs", "", "core",
     "Strains of bacteria that are resistant to multiple antibiotics, making infections hard to treat."),
    ("misuse", "Misuse of Antimicrobials", "", "core",
     "Incorrect use of medicines, such as wrong drug choice, wrong dose, overuse, or stopping treatment too early."),
    ("stewardship", "Antimicrobial Stewardship", "", "core",
     "Coordinated strategies to use antimicrobials wisely and responsibly to preserve their effectiveness."),
    ("ipc", "Infection Prevention and Control", "IPC", "core",
     "Measures like hand hygiene, vaccination, safe hospital practices, and clean environments to prevent the spread of infections, including resistant ones."),
    ("one-health", "One Health Approach", "", "core",
     "A strategy recognizing the interconnection between human health, animal health, and the environment in tackling AMR."),

    ("mdr", "Multidrug-Resistant", "MDR", "technical",
     "Microorganisms resistant to at least one medicine in three or more antimicrobial categories."),
    ("xdr", "Extensively Drug-Resistant", "XDR", "technical",
     "Resistant to almost all available antimicrobials, with only a few treatment options left."),
    ("pdr", "Pan-Drug Resistant", "PDR", "technical",
     "Resistant to all known antimicrobials, leaving no effective treatments."),
    ("last-resort", "Last-Resort Antibiotics", "", "technical",
     "Potent antibiotics (like colistin or carbapenems) reserved for infections that don't respond to other treatments."),
    ("nosocomial", "Nosocomial Infections (Hospital-Acquired Infections)", "HAI", "technical",
     "Infections acquired in healthcare settings, often involving resistant pathogens."),
    ("surveillance", "Surveillance", "", "technical",
     "The systematic monitoring of AMR trends in humans, animals, and the environment to guide interventions."),

    ("resistance-genes", "Resistance Genes", "", "genetics",
     "Segments of DNA that provide microorganisms with the ability to survive treatment with antimicrobials."),
    ("hgt", "Horizontal Gene Transfer", "HGT", "genetics",
     "The process by which bacteria exchange genetic material (including resistance genes) with one another."),
    ("plasmid", "Plasmid", "", "genetics",
     "Small, circular DNA molecules in bacteria that often carry and transfer resistance genes between cells."),
    ("efflux-pump", "Efflux Pump", "", "genetics",
     "Protein systems that bacteria use to pump antimicrobial drugs out of their cells before the drugs can act."),
    ("integrons", "Integrons", "", "genetics",
     "Genetic elements that capture, store, and express resistance genes, contributing to the spread of AMR."),
    ("transposons", "Transposons (“Jumping Genes”)", "", "genetics",
     "DNA sequences that can move within and between genomes, spreading resistance traits."),
    ("mutation", "Mutation", "", "genetics",
     "A permanent change in DNA sequence that can create or enhance resistance."),
    ("mge", "Mobile Genetic Elements", "MGEs", "genetics",
     "Pieces of DNA (like plasmids, transposons, and integrons) that move between organisms, helping spread resistance."),

    ("selective-pressure", "Selective Pressure", "", "additional",
     "The survival advantage microorganisms gain when exposed to antimicrobials, allowing resistant ones to thrive while others die off."),
    ("biofilm", "Biofilm", "", "additional",
     "A protective layer formed by communities of microbes that makes them more resistant to antimicrobials and immune responses."),
    ("intrinsic-resistance", "Intrinsic Resistance", "", "additional",
     "Natural resistance that certain microorganisms already have, without needing new mutations or gene acquisition."),
    ("acquired-resistance", "Acquired Resistance", "", "additional",
     "Resistance developed through mutations or by picking up resistance genes from other microbes."),
    ("gap", "Global Action Plan", "GAP", "additional",
     "The World Health Organization's framework to guide countries in combating AMR."),
]


def seed(apps, schema_editor):
    GlossaryCategory = apps.get_model("main", "GlossaryCategory")
    GlossaryTerm = apps.get_model("main", "GlossaryTerm")

    categories = {}
    for slug, name, icon, description, order in CATEGORIES:
        category, _ = GlossaryCategory.objects.get_or_create(
            slug=slug,
            defaults={"name": name, "icon": icon, "description": description, "order": order},
        )
        categories[slug] = category

    for slug, term, abbreviation, category_slug, definition in TERMS:
        if GlossaryTerm.objects.filter(slug=slug).exists() or GlossaryTerm.objects.filter(term=term).exists():
            continue
        GlossaryTerm.objects.create(
            slug=slug,
            term=term,
            abbreviation=abbreviation,
            category=categories[category_slug],
            definition=definition,
            approval_status="approved",
            is_active=True,
        )


def unseed(apps, schema_editor):
    GlossaryCategory = apps.get_model("main", "GlossaryCategory")
    GlossaryTerm = apps.get_model("main", "GlossaryTerm")
    GlossaryTerm.objects.filter(slug__in=[t[0] for t in TERMS]).delete()
    GlossaryCategory.objects.filter(slug__in=[c[0] for c in CATEGORIES], terms__isnull=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0007_glossary"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
