import argparse

from .. import ontology
from ._base import Command


class OntologyCommand(Command):
    name = "ontology"
    help = "Navigate the cached Diffbot ontology (types, fields, taxonomies, enums)."

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        sub = parser.add_subparsers(dest="action", required=True, metavar="ACTION")

        sub.add_parser("types", help="List all entity type names.")
        sub.add_parser("composites", help="List all composite type names.")
        sub.add_parser("enums", help="List all enum type names.")
        sub.add_parser("taxonomies", help="List all taxonomy names.")

        p_fields = sub.add_parser(
            "fields",
            help="List fields of an entity type or composite. e.g. dql ontology fields Organization",
        )
        p_fields.add_argument("type", help="Entity type or composite name (e.g. Organization, Location)")
        p_fields.add_argument("search", nargs="?", default=None, help="Optional case-insensitive regex to filter field names")
        p_fields.add_argument("--include-deprecated", action="store_true")

        p_tax = sub.add_parser("taxonomy", help="List values of a taxonomy.")
        p_tax.add_argument("name", help="Taxonomy name (e.g. OrganizationCategory)")
        p_tax.add_argument("search", nargs="?", default=None, help="Optional case-insensitive regex")

        p_enum = sub.add_parser("enum", help="List values of an enum.")
        p_enum.add_argument("name", help="Enum name (e.g. Language)")

        p_search = sub.add_parser(
            "search",
            help="Generic fallback: search every 'name' field in the ontology by regex.",
        )
        p_search.add_argument("term", help="Case-insensitive regex")

    def run(self, args: argparse.Namespace) -> int:
        action = args.action
        if action == "types":
            for n in ontology.list_types():
                print(n)
        elif action == "composites":
            for n in ontology.list_composites():
                print(n)
        elif action == "enums":
            for n in ontology.list_enums():
                print(n)
        elif action == "taxonomies":
            for n in ontology.list_taxonomies():
                print(n)
        elif action == "fields":
            fields = ontology.fields_for(args.type)
            for name, meta in ontology.filter_fields(fields, args.search, include_deprecated=args.include_deprecated):
                print(ontology.format_field(name, meta))
        elif action == "taxonomy":
            for v in ontology.taxonomy_values(args.name, args.search):
                print(v)
        elif action == "enum":
            for v in ontology.enum_values(args.name):
                print(v)
        elif action == "search":
            for n in ontology.find_named(args.term):
                print(n)
        return 0


COMMAND = OntologyCommand()
