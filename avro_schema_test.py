import fastavro

schema = {
  "type": "record",
  "name": "User",
  "namespace": "com.example",
  "fields": [
    {
      "name": "name",
      "type": "string",
      "doc": "Name of the user"
    },
    {
      "name": "age",
      "type": "int",
      "doc": "Age of the user",
      "cid": True
    },
    {
      "name": "gender",
      "type": "string",
      "doc": "Gender of the user",
      "deprecated": True
    }
  ]
}

# Parse the schema
parsed_schema = fastavro.parse_schema(schema)

# Access the custom tags
for field in parsed_schema['fields']:
    print(f"Field name: {field['name']}")
    for key, value in field.items():
        if key not in ['name', 'type', 'doc']:
            print(f"  {key}: {value}")
