from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from django.db import connection, transaction
from django.utils import timezone
from django_tenants.utils import schema_context, tenant_context
from apps.tenants.models import Tenant, Domain
from apps.contacts.models import Company, Contact
from apps.demo.models import DemoRequest
from apps.platform.models import SuperUser
from apps.users.models import CustomUser
from apps.opportunities.models import SalesStage, Opportunity, OpportunityHistory
from apps.activities.models import ActivityType, Activity, Task, InteractionLog
import random
from decimal import Decimal
from datetime import timedelta, date

# For public schema (platform)
PlatformUser = SuperUser
# For tenant schemas
TenantUser = CustomUser


class Command(BaseCommand):
    help = 'Complete seed data: creates superuser, tenant with users, groups, permissions, and sample data including opportunities'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🌱 Starting comprehensive seed...'))
        
        with transaction.atomic():
            # Step 1: Create superuser (in public schema)
            superuser_credentials = self.create_superuser()
            
            # Step 2: Create tenant and domain
            tenant = self.create_tenant()
            
            # Step 3: Switch to tenant schema and create tenant data
            with tenant_context(tenant):
                tenant_admin_credentials = self.create_tenant_data()
                
                # Step 4: Create sales stages (including default stages)
                self.create_sales_stages()
                
                # Step 5: Create sample business data (including opportunities)
                self.create_sample_data()

                self.create_activity_types()

                self.create_activities_and_tasks()
        
        # Print credentials at the end
        self.print_credentials(superuser_credentials, tenant_admin_credentials)
        
        self.stdout.write(self.style.SUCCESS('🎉 Comprehensive seed completed successfully!'))

    def create_superuser(self):
        """Create platform superuser"""
        self.stdout.write('👑 Creating platform superuser...')
        
        # Check if superuser already exists
        if PlatformUser.objects.filter(email='admin@platform.com').exists():
            self.stdout.write('⏭️  Superuser already exists')
            return {
                'email': 'admin@platform.com',
                'password': '****existing****'
            }
        
        superuser = PlatformUser.objects.create_superuser(
            email='admin@platform.com',
            password='platform123',
            first_name='Platform',
            last_name='Administrator'
        )
        
        self.stdout.write(f'✅ Created superuser: {superuser.email}')
        return {
            'email': 'admin@platform.com',
            'password': 'platform123'
        }

    def create_tenant(self):
        """Create tenant and domain"""
        self.stdout.write('🏢 Creating tenant and domain...')
        
        # Create or get tenant
        tenant, created = Tenant.objects.get_or_create(
            schema_name='acme',
            defaults={
                'name': 'ACME Corporation',
                'contact_email': 'admin@acme.com',
                'industry': 'Technology',
                'company_size': '51-200'
            }
        )
        
        if created:
            self.stdout.write(f'✅ Created tenant: {tenant.name}')
        else:
            self.stdout.write(f'⏭️  Tenant {tenant.name} already exists')
        
        # Create or get domain
        domain, created = Domain.objects.get_or_create(
            domain='acme.localhost',
            defaults={
                'tenant': tenant,
                'is_primary': True
            }
        )
        
        if created:
            self.stdout.write(f'✅ Created domain: {domain.domain}')
        else:
            self.stdout.write(f'⏭️  Domain {domain.domain} already exists')
        
        return tenant

    def create_tenant_data(self):
        """Create groups, permissions, and users in tenant schema"""
        self.stdout.write('👥 Creating tenant groups and users...')
        
        # Create groups with different permission levels
        groups = self.create_groups()
        
        # Create users and assign to groups
        admin_credentials = self.create_users(groups)
        
        return admin_credentials

    def create_groups(self):
        """Create tenant groups with appropriate permissions"""
        groups_data = {
            'Admin': {
                'description': 'Full tenant administration access',
                'permissions': 'all_tenant'
            },
            'Manager': {
                'description': 'Management level access',
                'permissions': 'management'
            },
            'Sales': {
                'description': 'Sales team access',
                'permissions': 'sales'
            },
            'Support': {
                'description': 'Customer support access',
                'permissions': 'support'
            },
            'User': {
                'description': 'Basic user access',
                'permissions': 'basic'
            }
        }
        
        created_groups = {}
        
        for group_name, group_info in groups_data.items():
            group, created = Group.objects.get_or_create(name=group_name)
            
            if created:
                self.assign_permissions_to_group(group, group_info['permissions'])
                self.stdout.write(f'✅ Created group: {group_name}')
            else:
                self.stdout.write(f'⏭️  Group {group_name} already exists')
            
            created_groups[group_name] = group
        
        return created_groups

    def assign_permissions_to_group(self, group, permission_level):
        """Assign permissions based on the permission level"""
        all_permissions = Permission.objects.all()
        
        if permission_level == 'all_tenant':
            # Admin gets all tenant permissions except superuser-only ones
            tenant_permissions = all_permissions.exclude(
                codename__in=[
                    'add_tenant', 'change_tenant', 'delete_tenant', 'view_tenant',
                    'add_domain', 'change_domain', 'delete_domain', 'view_domain',
                ]
            )
            group.permissions.set(tenant_permissions)
            
        elif permission_level == 'management':
            # Managers get user and content management permissions
            manager_permissions = all_permissions.filter(
                codename__in=[
                    'view_customuser', 'add_customuser', 'change_customuser',
                    'view_contact', 'add_contact', 'change_contact', 'delete_contact',
                    'view_company', 'add_company', 'change_company', 'delete_company',
                    'view_opportunity', 'add_opportunity', 'change_opportunity', 'delete_opportunity',
                    'view_salesstage', 'add_salesstage', 'change_salesstage',
                    'view_opportunityhistory',
                ]
            )
            group.permissions.set(manager_permissions)
            
        elif permission_level == 'sales':
            # Sales team gets contact and opportunity permissions
            sales_permissions = all_permissions.filter(
                codename__in=[
                    'view_contact', 'add_contact', 'change_contact',
                    'view_company', 'add_company', 'change_company',
                    'view_opportunity', 'add_opportunity', 'change_opportunity',
                    'view_salesstage',
                    'view_opportunityhistory', 'add_opportunityhistory',
                ]
            )
            group.permissions.set(sales_permissions)
            
        elif permission_level == 'support':
            # Support gets view/change permissions for contacts
            support_permissions = all_permissions.filter(
                codename__in=[
                    'view_contact', 'change_contact',
                    'view_company',
                    'view_opportunity',
                    'view_opportunityhistory',
                ]
            )
            group.permissions.set(support_permissions)
            
        elif permission_level == 'basic':
            # Basic users get view-only permissions
            basic_permissions = all_permissions.filter(
                codename__in=[
                    'view_contact',
                    'view_company',
                    'view_opportunity',
                    'view_opportunityhistory',
                ]
            )
            group.permissions.set(basic_permissions)

    def create_users(self, groups):
        """Create sample users and assign to groups"""
        users_data = [
            {
                'email': 'admin@acme.com',
                'password': 'admin123',
                'first_name': 'Admin',
                'last_name': 'User',
                'groups': ['Admin'],
                'is_admin': True,
            },
            {
                'email': 'manager@acme.com',
                'password': 'manager123',
                'first_name': 'Sales',
                'last_name': 'Manager',
                'groups': ['Manager'],
            },
            {
                'email': 'alice.sales@acme.com',
                'password': 'alice123',
                'first_name': 'Alice',
                'last_name': 'Johnson',
                'groups': ['Sales'],
            },
            {
                'email': 'bob.sales@acme.com',
                'password': 'bob123',
                'first_name': 'Bob',
                'last_name': 'Smith',
                'groups': ['Sales'],
            },
            {
                'email': 'support@acme.com',
                'password': 'support123',
                'first_name': 'Support',
                'last_name': 'Agent',
                'groups': ['Support'],
            },
        ]
        
        created_users = []
        admin_credentials = None
        
        for user_data in users_data:
            # Check if user already exists
            if TenantUser.objects.filter(email=user_data['email']).exists():
                self.stdout.write(f'⏭️  User {user_data["email"]} already exists')
                continue
            
            # Create user
            user = TenantUser.objects.create_user(
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                is_admin=user_data.get('is_admin', False),
            )
            
            # Assign to groups
            for group_name in user_data['groups']:
                if group_name in groups:
                    user.groups.add(groups[group_name])
            
            created_users.append(user)
            self.stdout.write(f'✅ Created user: {user.email}')
            
            # Store admin credentials
            if user_data['email'] == 'admin@acme.com':
                admin_credentials = {
                    'email': user_data['email'],
                    'password': user_data['password']
                }
        
        return admin_credentials or {
            'email': 'admin@acme.com',
            'password': '****existing****'
        }

    def create_sales_stages(self):
        """Create default sales stages using the create_default_stages logic"""
        self.stdout.write('📈 Creating sales stages...')
        
        # Check if stages already exist
        if SalesStage.objects.exists():
            self.stdout.write('⏭️  Sales stages already exist')
            return
        
        # Use the same default stages from the create_default_stages view
        default_stages = [
            {
                'name': 'Lead',
                'description': 'Initial contact, unqualified lead',
                'order': 1,
                'probability': 10,
                'color': '#64748b'
            },
            {
                'name': 'Qualified',
                'description': 'Lead has been qualified and shows interest',
                'order': 2,
                'probability': 25,
                'color': '#3b82f6'
            },
            {
                'name': 'Proposal',
                'description': 'Proposal or quote has been sent',
                'order': 3,
                'probability': 50,
                'color': '#8b5cf6'
            },
            {
                'name': 'Negotiation',
                'description': 'In active negotiation phase',
                'order': 4,
                'probability': 75,
                'color': '#f59e0b'
            },
            {
                'name': 'Closed Won',
                'description': 'Deal successfully closed',
                'order': 5,
                'probability': 100,
                'color': '#10b981',
                'is_closed_won': True
            },
            {
                'name': 'Closed Lost',
                'description': 'Deal was lost or cancelled',
                'order': 6,
                'probability': 0,
                'color': '#ef4444',
                'is_closed_lost': True
            }
        ]
        
        # Get the admin user for created_by field
        admin_user = TenantUser.objects.filter(email='admin@acme.com').first()
        
        created_stages = []
        for stage_data in default_stages:
            stage = SalesStage.objects.create(
                name=stage_data['name'],
                description=stage_data['description'],
                order=stage_data['order'],
                probability=stage_data['probability'],
                color=stage_data['color'],
                is_closed_won=stage_data.get('is_closed_won', False),
                is_closed_lost=stage_data.get('is_closed_lost', False),
                created_by=admin_user
            )
            created_stages.append(stage)
            self.stdout.write(f'✅ Created stage: {stage.name}')
        
        self.stdout.write(f'📈 Created {len(created_stages)} default sales stages')

    def create_sample_data(self):
        """Create sample companies, contacts, and opportunities"""
        self.stdout.write('📊 Creating sample business data...')
        
        # Check if sample data already exists
        if Company.objects.exists():
            self.stdout.write('⏭️  Sample data already exists')
            return
        
        # Get users for assignment
        admin_user = TenantUser.objects.filter(email='admin@acme.com').first()
        sales_users = list(TenantUser.objects.filter(groups__name='Sales'))
        manager_user = TenantUser.objects.filter(email='manager@acme.com').first()
        
        if not sales_users:
            sales_users = [admin_user] if admin_user else []
        
        # IMPORTANT FIX: Update admin user properties to fix JWT authentication
        if admin_user:
            # The issue is that CustomUser.is_staff and is_superuser return False
            # But JWT authentication relies on these properties
            # We need to ensure the admin user works properly with JWT tokens
            self.fix_admin_user_authentication(admin_user)
        
        # Get sales stages
        stages = list(SalesStage.objects.all().order_by('order'))
        if not stages:
            self.stdout.write('❌ No sales stages found. Cannot create opportunities.')
            return
        
        # Sample companies data
        companies_data = [
            {
                'name': 'TechStart Solutions',
                'industry': 'Technology',
                'size': '11-50',
                'website': 'https://techstart.com',
                'notes': 'Innovative startup focused on AI solutions'
            },
            {
                'name': 'Global Manufacturing Inc',
                'industry': 'Manufacturing',
                'size': '201-500',
                'website': 'https://globalmfg.com',
                'notes': 'Leading manufacturer of industrial equipment'
            },
            {
                'name': 'HealthCare Plus',
                'industry': 'Healthcare',
                'size': '51-200',
                'website': 'https://healthcareplus.com',
                'notes': 'Healthcare technology and services provider'
            },
            {
                'name': 'EduTech Innovations',
                'industry': 'Education',
                'size': '11-50',
                'website': 'https://edutech.com',
                'notes': 'Educational technology solutions'
            },
            {
                'name': 'RetailMax Corp',
                'industry': 'Retail',
                'size': '500+',
                'website': 'https://retailmax.com',
                'notes': 'Large retail chain with online presence'
            }
        ]
        
        # Create companies and contacts
        created_companies = []
        created_contacts = []
        
        for i, company_data in enumerate(companies_data):
            # Create company
            company = Company.objects.create(
                name=company_data['name'],
                industry=company_data['industry'],
                size=company_data['size'],
                website=company_data['website'],
                notes=company_data['notes'],
                created_by=admin_user
            )
            created_companies.append(company)
            self.stdout.write(f'✅ Created company: {company.name}')
            
            # Create 2-3 contacts per company
            contacts_lists = [
                # TechStart Solutions
                [
                    {
                        'first_name': 'Alex',
                        'last_name': 'Rodriguez',
                        'job_title': 'CEO',
                        'contact_type': 'client'
                    },
                    {
                        'first_name': 'Sarah',
                        'last_name': 'Chen',
                        'job_title': 'CTO',
                        'contact_type': 'prospect'
                    },
                    {
                        'first_name': 'Marcus',
                        'last_name': 'Williams',
                        'job_title': 'Product Manager',
                        'contact_type': 'lead'
                    }
                ],
                # Global Manufacturing Inc
                [
                    {
                        'first_name': 'Jennifer',
                        'last_name': 'Thompson',
                        'job_title': 'Operations Director',
                        'contact_type': 'client'
                    },
                    {
                        'first_name': 'Robert',
                        'last_name': 'Davis',
                        'job_title': 'VP Engineering',
                        'contact_type': 'prospect'
                    },
                    {
                        'first_name': 'Lisa',
                        'last_name': 'Anderson',
                        'job_title': 'Procurement Manager',
                        'contact_type': 'lead'
                    }
                ],
                # HealthCare Plus
                [
                    {
                        'first_name': 'David',
                        'last_name': 'Martinez',
                        'job_title': 'Chief Medical Officer',
                        'contact_type': 'client'
                    },
                    {
                        'first_name': 'Emily',
                        'last_name': 'Brown',
                        'job_title': 'IT Director',
                        'contact_type': 'prospect'
                    },
                    {
                        'first_name': 'Mike',
                        'last_name': 'Johnson',
                        'job_title': 'Purchase Manager',
                        'contact_type': 'lead'
                    }
                ],
                # EduTech Innovations
                [
                    {
                        'first_name': 'Amanda',
                        'last_name': 'Wilson',
                        'job_title': 'Head of Technology',
                        'contact_type': 'client'
                    },
                    {
                        'first_name': 'James',
                        'last_name': 'Taylor',
                        'job_title': 'Academic Director',
                        'contact_type': 'prospect'
                    },
                    {
                        'first_name': 'Rachel',
                        'last_name': 'Green',
                        'job_title': 'Innovation Lead',
                        'contact_type': 'lead'
                    }
                ],
                # RetailMax Corp
                [
                    {
                        'first_name': 'Christopher',
                        'last_name': 'Lee',
                        'job_title': 'VP Digital',
                        'contact_type': 'client'
                    },
                    {
                        'first_name': 'Michelle',
                        'last_name': 'White',
                        'job_title': 'Store Operations',
                        'contact_type': 'prospect'
                    },
                    {
                        'first_name': 'Kevin',
                        'last_name': 'Garcia',
                        'job_title': 'Technology Manager',
                        'contact_type': 'lead'
                    }
                ]
            ]
            
            # Get unique contacts for this company
            contacts_for_company = contacts_lists[i]

            company_contacts = []
            for j, contact_data in enumerate(contacts_for_company):
                if j < 2 or random.random() > 0.5:  # Create 2-3 contacts randomly
                    owner = random.choice(sales_users) if sales_users else admin_user
                    contact = Contact.objects.create(
                        first_name=contact_data['first_name'],
                        last_name=contact_data['last_name'],
                        email=f"{contact_data['first_name'].lower()}.{contact_data['last_name'].lower()}@{company.name.lower().replace(' ', '').replace('.', '')}.com",
                        phone=f'+1-555-{1000 + i*10 + j}',  # Unique phone numbers
                        job_title=contact_data.get('job_title', ''),
                        company=company,
                        contact_type=contact_data['contact_type'],
                        owner=owner,
                        created_by=admin_user
                    )
                    company_contacts.append(contact)
                    created_contacts.append(contact)
                    self.stdout.write(f'✅ Created contact: {contact.full_name}')
            
            # Create 1-2 opportunities per company
            for j in range(random.randint(1, 2)):
                self.create_sample_opportunity(company, company_contacts, stages, sales_users, admin_user)
        
        self.stdout.write(f'📊 Created {len(created_companies)} companies and {len(created_contacts)} contacts')

    def create_sample_opportunity(self, company, contacts, stages, sales_users, admin_user):
        """Create a sample opportunity for a company"""
        if not contacts:
            return
        
        opportunity_names = [
            f"Q1 Software License - {company.name}",
            f"Enterprise Solution - {company.name}",
            f"Annual Service Contract - {company.name}",
            f"Technology Upgrade - {company.name}",
            f"Consulting Services - {company.name}"
        ]
        
        # Random opportunity data
        name = random.choice(opportunity_names)
        contact = random.choice(contacts)
        stage = random.choice(stages[:-2])  # Exclude closed stages for active opportunities
        owner = random.choice(sales_users) if sales_users else admin_user
        value = Decimal(str(random.randint(5000, 100000)))
        
        # Random priority
        priorities = ['low', 'medium', 'high', 'urgent']
        priority = random.choice(priorities)
        
        # Expected close date (1-6 months from now)
        days_ahead = random.randint(30, 180)
        expected_close = timezone.now().date() + timedelta(days=days_ahead)
        
        # Create opportunity
        opportunity = Opportunity.objects.create(
            name=name,
            description=f"Sales opportunity for {company.name} involving our enterprise solutions.",
            value=value,
            contact=contact,
            company=company,
            stage=stage,
            owner=owner,
            priority=priority,
            probability=stage.probability,
            expected_close_date=expected_close,
            created_by=admin_user
        )
        
        # Create initial history entry
        OpportunityHistory.objects.create(
            opportunity=opportunity,
            action='created',
            new_stage=stage,
            new_value=value,
            new_probability=stage.probability,
            changed_by=admin_user,
            notes=f'Opportunity created and assigned to {stage.name} stage'
        )
        
        self.stdout.write(f'✅ Created opportunity: {opportunity.name} (${value})')
        
        # Randomly create some stage changes for realism
        if random.random() > 0.7:  # 30% chance of stage progression
                            self.create_opportunity_progression(opportunity, stages, owner)

    def fix_admin_user_authentication(self, admin_user):
        """
        Fix authentication issues with admin users.
        The CustomUser model returns False for is_staff and is_superuser properties,
        but JWT authentication expects these to work properly.
        """
        self.stdout.write('🔧 Fixing admin user authentication...')
        
        # Ensure the admin user has the proper admin status
        if not admin_user.is_admin:
            admin_user.is_admin = True
            admin_user.save()
            self.stdout.write('✅ Updated admin user is_admin status')
        
        # Verify the user has proper permissions by adding them to all groups
        from django.contrib.auth.models import Group
        admin_group = Group.objects.filter(name='Admin').first()
        if admin_group and admin_group not in admin_user.groups.all():
            admin_user.groups.add(admin_group)
            self.stdout.write('✅ Added admin user to Admin group')
        
        # The core issue is in the CustomUser model properties:
        # @property
        # def is_staff(self):
        #     return False  # This breaks JWT authentication!
        # 
        # @property 
        # def is_superuser(self):
        #     return False  # This also breaks JWT authentication!
        #
        # These should return self.is_admin instead of False for admin users
        self.stdout.write('⚠️  Note: JWT authentication issues are due to CustomUser model properties')
        self.stdout.write('    is_staff and is_superuser return False, breaking authentication')
        self.stdout.write('    This needs to be fixed in apps/users/models.py')

    def create_opportunity_progression(self, opportunity, stages, owner):
        """Create realistic progression history for an opportunity"""
        current_stage_index = next((i for i, stage in enumerate(stages) if stage == opportunity.stage), 0)
        
        # Calculate maximum possible progression steps safely
        max_possible_steps = len(stages) - current_stage_index - 3  # Leave room before closed stages
        
        # Ensure we have a valid range for progression steps
        if max_possible_steps <= 0:
            # If we're already near the end stages, don't create progression
            return
        
        # Safe range calculation
        max_steps = min(2, max_possible_steps)
        if max_steps <= 0:
            return
            
        progression_steps = random.randint(1, max_steps)
        
        # Start from Lead stage (index 0) and progress forward
        current_date = timezone.now() - timedelta(days=random.randint(30, 90))
        
        for step in range(progression_steps):
            stage_index = min(step, len(stages) - 3)  # Don't go to closed stages
            stage = stages[stage_index]
            
            # Create history entry
            OpportunityHistory.objects.create(
                opportunity=opportunity,
                stage=stage,
                changed_by=owner,
                changed_at=current_date,
                notes=f"Opportunity progressed to {stage.name} stage"
            )
            
            # Move to next date
            current_date += timedelta(days=random.randint(7, 21))
        
        self.stdout.write(f'📊 Created {progression_steps} progression steps for {opportunity.name}')

    def create_activity_types(self):
        """Create default activity types"""
        self.stdout.write('🎯 Creating activity types...')
        
        activity_types_data = [
            {
                'name': 'Call',
                'description': 'Phone call with contact',
                'icon': 'phone',
                'color': '#10b981',
                'requires_duration': True,
                'requires_outcome': True
            },
            {
                'name': 'Email',
                'description': 'Email communication',
                'icon': 'mail',
                'color': '#3b82f6',
                'requires_duration': False,
                'requires_outcome': False
            },
            {
                'name': 'Meeting',
                'description': 'In-person or virtual meeting',
                'icon': 'users',
                'color': '#8b5cf6',
                'requires_duration': True,
                'requires_outcome': True
            },
            {
                'name': 'Demo',
                'description': 'Product demonstration',
                'icon': 'monitor',
                'color': '#f59e0b',
                'requires_duration': True,
                'requires_outcome': True
            },
            {
                'name': 'Follow-up',
                'description': 'Follow-up activity',
                'icon': 'clock',
                'color': '#ef4444',
                'requires_duration': False,
                'requires_outcome': True
            }
        ]
        
        created_types = []
        for type_data in activity_types_data:
            activity_type = ActivityType.objects.create(**type_data)
            created_types.append(activity_type)
            self.stdout.write(f'✅ Created activity type: {activity_type.name}')
        
        return created_types

    def create_activities_and_tasks(self):
        """Create sample activities and tasks"""
        self.stdout.write('📅 Creating sample activities and tasks...')
        
        # Get required data
        activity_types = list(ActivityType.objects.all())
        contacts = list(Contact.objects.all())
        companies = list(Company.objects.all())
        opportunities = list(Opportunity.objects.all())
        users = list(TenantUser.objects.all())
        
        if not activity_types or not contacts:
            self.stdout.write('⏭️ No activity types or contacts found, skipping activities creation')
            return
        
        # Create sample activities
        for i in range(10):
            contact = random.choice(contacts)
            activity_type = random.choice(activity_types)
            assigned_user = random.choice(users)
            
            # Random scheduled time (next 30 days)
            days_ahead = random.randint(1, 30)
            hours = random.randint(9, 17)  # Business hours
            scheduled_at = timezone.now() + timedelta(days=days_ahead, hours=hours-timezone.now().hour)
            
            activity = Activity.objects.create(
                title=f"{activity_type.name} with {contact.first_name} {contact.last_name}",
                description=f"Scheduled {activity_type.name.lower()} to discuss business opportunities",
                activity_type=activity_type,
                scheduled_at=scheduled_at,
                duration_minutes=random.choice([30, 45, 60]) if activity_type.requires_duration else None,
                priority=random.choice(['low', 'medium', 'high']),
                status=random.choice(['scheduled', 'completed']) if i < 5 else 'scheduled',
                contact=contact,
                company=contact.company,
                opportunity=random.choice(opportunities) if opportunities else None,
                assigned_to=assigned_user,
                created_by=users[0],  # Admin user
            )
            
            self.stdout.write(f'✅ Created activity: {activity.title}')
        
        # Create sample tasks
        for i in range(8):
            contact = random.choice(contacts)
            assigned_user = random.choice(users)
            
            # Random due date (next 14 days)
            days_ahead = random.randint(1, 14)
            due_date = timezone.now() + timedelta(days=days_ahead)
            
            task = Task.objects.create(
                title=f"Follow up on {contact.company.name} proposal",
                description=f"Review and follow up on the proposal sent to {contact.first_name} {contact.last_name}",
                priority=random.choice(['low', 'medium', 'high', 'urgent']),
                due_date=due_date,
                status=random.choice(['todo', 'in_progress']) if i < 6 else 'completed',
                assigned_to=assigned_user,
                created_by=users[0],  # Admin user
                contact=contact,
                company=contact.company,
                opportunity=random.choice(opportunities) if opportunities else None,
            )
            
            # Mark some as completed
            if task.status == 'completed':
                task.completed_at = timezone.now() - timedelta(days=random.randint(1, 5))
                task.completion_notes = "Task completed successfully"
                task.save()
            
            self.stdout.write(f'✅ Created task: {task.title}')

    def print_credentials(self, superuser_creds, tenant_admin_creds):
        """Print login credentials at the end"""
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('🔑 LOGIN CREDENTIALS'))
        self.stdout.write('=' * 50)
        
        self.stdout.write(self.style.WARNING('PLATFORM ADMIN (Public Schema):'))
        self.stdout.write(f'  URL: http://localhost:8000/admin/')
        self.stdout.write(f'  Email: {superuser_creds["email"]}')
        self.stdout.write(f'  Password: {superuser_creds["password"]}')
        
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('TENANT ADMIN (ACME Corp):'))
        self.stdout.write(f'  URL: http://acme.localhost:8000/')
        self.stdout.write(f'  Email: {tenant_admin_creds["email"]}')
        self.stdout.write(f'  Password: {tenant_admin_creds["password"]}')
        
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('OTHER TENANT USERS:'))
        self.stdout.write('  manager@acme.com / manager123 (Manager)')
        self.stdout.write('  alice.sales@acme.com / alice123 (Sales)')
        self.stdout.write('  bob.sales@acme.com / bob123 (Sales)')
        self.stdout.write('  support@acme.com / support123 (Support)')
        
        self.stdout.write('')
        self.stdout.write('=' * 50)