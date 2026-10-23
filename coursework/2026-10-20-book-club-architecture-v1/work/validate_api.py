"""Static contract validation only; no live API is called."""
import copy
import hashlib
import json
from pathlib import Path

import yaml
from openapi_spec_validator import validate_spec
from openapi_schema_validator import OAS30Validator, oas30_format_checker

BASE=Path(__file__).resolve().parents[1]
path=BASE/'book-club.openapi.yaml'
spec=yaml.safe_load(path.read_text())
validate_spec(spec)
count=1
examples=0
rejected=0

def require(condition,message):
    global count
    if not condition: raise AssertionError(message)
    count+=1

def resolve(v):
    if isinstance(v,dict):
        if '$ref' in v:
            require(v['$ref'].startswith('#/'),'Local reference required')
            target=spec
            for item in v['$ref'][2:].split('/'): target=target[item.replace('~1','/').replace('~0','~')]
            return resolve(target)
        return {k:resolve(x) for k,x in v.items()}
    if isinstance(v,list): return [resolve(x) for x in v]
    return v

def validator(schema):
    return OAS30Validator(resolve(schema),format_checker=oas30_format_checker)

def check_example(schema,value):
    global examples
    validator(schema).validate(value)
    examples+=1

def visit(v):
    if isinstance(v,dict):
        if 'schema' in v:
            if 'example' in v: check_example(v['schema'],v['example'])
            for example in v.get('examples',{}).values():
                if 'value' in example: check_example(v['schema'],example['value'])
        for x in v.values(): visit(x)
    elif isinstance(v,list):
        for x in v: visit(x)

visit(spec)
schemas=spec['components']['schemas']
for name,schema in schemas.items(): check_example(schema,schema['example'])
require(set(spec['paths'])=={'/meetings','/meetings/{id}/registrations'},'Exactly the two assigned endpoints')
get=spec['paths']['/meetings']['get']
post=spec['paths']['/meetings/{id}/registrations']['post']
require(set(get['responses'])=={'200','400'},'GET statuses')
require(set(post['responses'])=={'201','400','404','409'},'POST statuses')
require(get['parameters'][0]['name']=='from' and get['parameters'][0]['required'] is False,'Optional from query')
require(post['parameters'][0]['in']=='path' and post['parameters'][0]['required'],'Required path id')
require(post['requestBody']['required'],'Required request body')
require(set(post['responses']['409']['content']['application/json']['examples'])=={'alreadyRegistered','meetingFull'},'Both conflict examples')
negative=[
    (schemas['RegistrationRequest'],{}),
    (schemas['RegistrationRequest'],{'participantId':0}),
    (schemas['RegistrationRequest'],{'participantId':'7'}),
    (schemas['RegistrationRequest'],{'participantId':7,'admin':True}),
    (post['parameters'][0]['schema'],0),
    (get['parameters'][0]['schema'],'2026-13-99'),
    (schemas['Error'],{'code':'UNKNOWN','message':'error'}),
    (schemas['Registration'],{**schemas['Registration']['example'],'createdAt':'2026-11-01'}),
    (schemas['Meeting'],{**schemas['Meeting']['example'],'remainingSeats':-1}),
]
for schema,value in negative:
    require(not validator(schema).is_valid(value),'Invalid counterexample must be rejected')
    rejected+=1

require(schemas['Meeting']['example']['remainingSeats']<=schemas['Meeting']['example']['capacity'],'Example capacity invariant')
report={'openapi_version':spec['openapi'],'static_contract_validation':'PASS','checks':count,'valid_examples':examples,'rejected_counterexamples':rejected,'operations':2,'schemas':len(schemas),'business_execution':'NOT_RUN','sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
(BASE/'data/api-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report))
