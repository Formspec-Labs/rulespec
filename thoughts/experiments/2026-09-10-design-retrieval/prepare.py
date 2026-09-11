"""Freeze source-derived labels and saved provider books before any ranking."""
import hashlib,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent
INPUTS={
'leave':'examples/document_understanding/low-thinking-experiment/runs/leave-full-low-1/rulebook.json',
'alcohol':'thoughts/experiments/2026-09-10-evidence-catalog/inputs/alcohol/book.json',
'rail':'thoughts/experiments/2026-09-10-evidence-catalog/inputs/rail-crossings/book.json',
'refrigerants':'thoughts/experiments/2026-09-10-evidence-catalog/inputs/refrigerants/book.json'}
Q=[]
def q(id,source,query,kind,relevant,*context):
 Q.append(dict(id=id,source=source,query=query,kind=kind,relevant_quote=relevant,required_quotes=[relevant,*context]))
q('L1','leave','Must the 12 months employment be consecutive?','literal/omitted-passage','The 12 months an employee must have been employed by the employer need not be consecutive months, provided','Subject to the exceptions provided in paragraph (b)(2) of this section')
q('L2','leave','Returning after military service: does an old job still count toward leave eligibility?','paraphrase/exception','The employee\'s break in service is occasioned by the fulfillment of his or her Uniformed Services Employment and Reemployment Rights Act','Employment periods preceding a break in service of more than seven years must be counted','However, this section does not provide any greater entitlement to the employee than would be available under the USERRA')
q('L3','leave','Who has the burden of showing hours worked when records are inaccurate?','literal/actor','the employer has the burden of showing that the employee has not worked the requisite hours','In the event an employer does not maintain an accurate record of hours worked by an employee')
q('L4','leave','How many hours and employees nearby are needed to qualify for family leave?','paraphrase/conjunction','at least 1,250 hours of service during the 12-month period','at least 12 months, and','50 or more employees are employed by the employer within 75 miles')
q('L5','leave','Can leave be cancelled if staff numbers fall after it starts?','paraphrase/negative-control','an employer may not terminate employee leave that has already started if the employee count drops below 50')
q('A1','alcohol','Can a truck carry beer as cargo?','paraphrase/exception','Manifested and transported as part of a shipment','However, this does not apply to possession of wine, beer, or distilled spirits')
q('A2','alcohol','When must a driver report an order to the State if they request a review?','literal/alternative-deadline','within 30 days unless the driver chooses to request a review of the order','within 30 days of an affirmation of the order')
q('A3','alcohol','Deadline for a driver to appeal an out-of-service order in writing?','paraphrase/near-duplicate-deadlines','submitting a petition for review in writing within 10 days of the issuance of the order')
q('A4','alcohol','How long before going on duty is alcohol prohibited?','literal/near-duplicate-rules','within 4 hours before going on duty or operating')
q('R1','rail','Must the driver stop when a police officer directs traffic to proceed?','literal/parent-context','A railroad grade crossing when a police officer or crossing flagman directs traffic to proceed','A stop need not be made at:')
q('R2','rail','Does a green traffic light always permit skipping the railroad stop?','paraphrase/qualification','a functioning highway traffic signal transmitting a green indication','under local law, permits the commercial motor vehicle to proceed across the railroad tracks without slowing or stopping','A stop need not be made at:')
q('R3','rail','Who may authorize an Exempt sign at a spur line crossing?','paraphrase/actor','Such “Exempt” signs shall be erected only by or with the consent of the appropriate State or local authority')
q('R4','rail','Division 2.3 chlorine vehicle railroad crossing rules','literal/scope','Every commercial motor vehicle transporting any quantity of a Division 2.3 chlorine','Stops the commercial motor vehicle within 50 feet of, and not closer than 15 feet to, the tracks','The driver must not shift gears while crossing the tracks')
q('F1','refrigerants','When did the propane exemption start for refrigerated food dispensing equipment?','paraphrase/date-and-end-use','effective July 15, 2024, retail food refrigeration—refrigerated food processing and dispensing equipment','Propane (R-290)','the following substitutes in the following end-uses are exempt from this prohibition and from the requirements of this subpart')
q('F2','refrigerants','Are small accidental refrigerant releases during recovery always exempt?','paraphrase/good-faith-condition','good faith attempts to recycle or recover refrigerants','De minimis')
q('F3','refrigerants','What equipment must be used when servicing non-exempt refrigerant appliances?','literal/conjunction','No person may maintain, service, repair, or dispose of an appliance','certified')
books={k:json.loads(Path(p).read_text()) for k,p in INPUTS.items()}
# Last query wording comes from literal source, never output retrieval.
for x in Q:
 t=books[x['source']]['document']['text']
 for quote in x['required_quotes']:
  if quote not in t: raise ValueError((x['id'],quote,t[-1300:]))
(ROOT/'inputs').mkdir(exist_ok=True)
for name,path in INPUTS.items():
 with (ROOT/'inputs'/f'{name}.json').open('x') as f: json.dump(books[name],f,ensure_ascii=False,indent=2)
with (ROOT/'queries.json').open('x') as f: json.dump(Q,f,ensure_ascii=False,indent=2)
files=[ROOT/'PLAN.md',ROOT/'queries.json',*sorted((ROOT/'inputs').glob('*.json'))]
manifest={'provider_calls':0,'source_paths':INPUTS,'files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},'label_provenance':'agent-authored source-support questions; development corpus; not human gold'}
with (ROOT/'freeze.json').open('x') as f: json.dump(manifest,f,indent=2)
print('Frozen',len(Q),'queries and',len(books),'historical books')
