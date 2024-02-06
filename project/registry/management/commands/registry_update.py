from django.core.management.base import BaseCommand, CommandError
import os
import json
from django.conf import settings 
import datetime
import re
from urllib import request, parse
import csv
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

from registry.models import Operator, Region, Range 

from django import db
from pydantic import BaseModel

CSV_HEADERS = ('abc_def','sn_from','sn_to','capacity','operator','region','inn' )
class CSVRange(BaseModel):
    """ CSVRange validator model. """
    abc_def:int 
    sn_from:int 
    sn_to:int 
    capacity:int 
    operator: str
    region: str
    inn:int 




REGISTRY = getattr( settings, 'REGISTRY', False )

if REGISTRY == False:
    raise CommandError(
        """
        parameters of data import from the registry database are not specified 
        add the following lines to the settings 
        REGISTRY = {
            'registry_url'  :'https://opendata.digital.gov.ru/registry/numeric/downloads/',
            'config_file'   :'downloads/registry.json',
            'download_dir':'downloads',
        }"""
    )

class Command(BaseCommand):
    help = "update registry database"

    def add_arguments(self, parser):
        parser.add_argument( 
            "--pidfile", 
            default='registry_update.pid', 
            help="Delete poll instead of closing it",
        )


    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.init_config()
        self.today = str(datetime.date.today())
        self.operators = { operator.inn:operator for operator in Operator.objects.all() }
        self.regions = { region.name:region for region in Region.objects.all() }


    def upload_registry_list_data(self):
        registry_list_page = request.urlopen( REGISTRY['registry_url']  ).read().decode('utf-8')
        if registry_list_page:
            files = re.findall( '<a href="(.+?)" target="" class="text-primary-500 hover:text-primary-600"><button ', registry_list_page, re.UNICODE  )
            for file_url in files:
                a = parse.urlparse(file_url)
                csv_renge_file = os.path.basename(a.path)
                if csv_renge_file in self.config['file_list']:
                    pass
                else:
                    self.download_file(file_url, f'{REGISTRY["download_dir"]}/{csv_renge_file}')
                    self.config['file_list'].append(csv_renge_file)


    def truncate_and_load_registry_from_csv(self):
        """ обнавляются все диапазоны  
            так как база обновляется полностью очищаю таблиwу потом вставляю без проверок

            # TODO: могут потерятся всее данные при ошибки обновления 
            # TODO: процесс не очень быстрый возможно стоит сделать импорт CSV как файла в промежуточную таблицу и уже оттуда запросом  заполнять данные 
        """

        db_cursor = db.connection.cursor()
        db_cursor.execute( f'TRUNCATE {Range._meta.db_table} RESTART IDENTITY;' )

        for csv_renge_file in  self.config['file_list']:
            self.parce_csv_renge_file(f'{REGISTRY["download_dir"]}/{csv_renge_file}')

        db_cursor.execute( 'commit;' )


    def update_progress(self, progress):
        self.stdout.write('\r[{0}] {1}%'.format('#' * int(progress / 20), progress) , ending='')
        self.stdout.flush()
       
    def parce_csv_renge_file(self, file_name, batch_size=1000 ):

        self.stdout.write(self.style.HTTP_SUCCESS(f'parce csv file {file_name}') )
        self.stdout.flush()

        with open(file_name, encoding='utf-8') as f:
            row_count = sum(1 for row in f)

        if row_count == 0:
            self.stdout.write( self.style.SUCCESS('empty file'))
            return

        with open(file_name, encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='"')
            
            i = 0
            
            objs = []

            for row in reader:
                i+=1
                if i == 1: continue # пропускаю заголовки

                try:
                    row_dict = dict(zip(CSV_HEADERS, row))
                    csv_range = CSVRange(**row_dict)
                except:
                    # print('ERROR', row )
                    continue

                if csv_range.inn in self.operators:
                    operator = self.operators[csv_range.inn]
                else:
                    operator = Operator.objects.create(
                        name	 = csv_range.operator,
                        inn		 = csv_range.inn,
                    )
                    self.operators[operator.inn]=operator

                if csv_range.region in self.regions:
                    region = self.regions[csv_range.region]
                else:
                    region = Region.objects.create(
                        name	 = csv_range.region,
                    )
                    self.regions[csv_range.region]=region


                
                objs.append (Range(
                        abc_def=csv_range.abc_def,
                        sn_from=csv_range.sn_from,
                        sn_to=csv_range.sn_to,
                        operator=operator,
                        region=region,
                        capacity=csv_range.capacity,
                    )
                )

                if i % batch_size==0:
                    Range.objects.bulk_create(objs)
                    self.update_progress(int(i / row_count * 100))
                    objs = []

            if objs:
                Range.objects.bulk_create(objs)


        self.stdout.write( self.style.SUCCESS('\rOK                 '))


    def is_runing(self, pidfile):
        if os.path.isfile( pidfile ):
            fp = open( pidfile, "r" )

            pid_text = fp.readline().strip()
            if pid_text.isdigit():
                try:
                    pids = [pid for pid in os.listdir( '/proc' ) if pid.isdigit()]
                    if pid_text in pids:
                        self.stdout.write(
                            self.style.ERROR('process is already running: target pid {pid_text}')
                        )
                        return True
                except:# non-Linux?
                        pass      
        return False

    def download_file(self, file_url,file_name):
        self.stdout.write(self.style.HTTP_SUCCESS(f'download fle {file_url} .... ') , ending='')
        self.stdout.flush()
        request.urlretrieve(file_url,file_name)
        self.stdout.write( self.style.SUCCESS('OK'))
   
        return file_name

    def init_config(self):
        if os.path.exists(REGISTRY["config_file"]):
            with open(REGISTRY["config_file"], 'r') as f:
                self.config = json.load(f)
        else:
            self.config={
                'previos_run' : False,
                'file_list':[]
            }
        
    def save_config(self):
        with open(REGISTRY["config_file"], 'w') as f:
            json.dump(self.config, f)
        

    def handle(self, *args, **options):

        if "pidfile" in options and self.is_runing( options["pidfile"] ): 
            return False

        if self.config['previos_run']==self.today:
            self.stdout.write(
                self.style.HTTP_NOT_MODIFIED('Already updated today')
            )
            return False
        else:
            self.config['file_list'] = []


        self.upload_registry_list_data()


        if self.config['file_list']:
            self.truncate_and_load_registry_from_csv()


        self.config['previos_run'] = self.today
        self.save_config()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully')
        )






