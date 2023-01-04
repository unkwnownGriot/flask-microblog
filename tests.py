from datetime import datetime,timedelta
import unittest
from app import create_app , db
from app.models import User,Post
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class UserModelCase(unittest.TestCase):
    #the setup method create an apllication context and pushes it
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_password_hashing(self):
        u = User(username='suzan')
        u.set_password('dog')
        self.assertFalse(u.check_password('cat'))
        self.assertTrue(u.check_password('dog'))

    def test_avatar(self):
        u = User(username='john',email='john@gmail.com')
        self.assertEqual(u.avatar(128),('https://www.gravatar.com/avatar/'
        '1f9d9a9efc2f523b2f09629444632b5c?d=identicon&s=128'))
    
    def test_follow(self):
        u1 = User(username='john',email='john@gmail.com')
        u2 = User(username='suzan',email='suzan@gmail.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.followed.all(),[])
        self.assertEqual(u1.followers.all(),[])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(),1)
        self.assertEqual(u1.followed.first().username,'suzan')
        self.assertEqual(u2.followers.count(),1)
        self.assertEqual(u2.followers.first().username,'john')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(),0)
        self.assertEqual(u2.followers.count(),0)


    def test_follow_posts(self):
        #create four users
        u1 = User(username='john',email='john@gmail.com')
        u2 = User(username='suzan',email='suzan@gmail.com')
        u3 = User(username='edo',email='edo@gmail.com')
        u4 = User(username='togo',email='togo@gmail.com')
        db.session.add_all([u1,u2,u3,u4])

        #create four posts
        now = datetime.utcnow()
        p1 = Post(body='Post from john', author=u1,timestamp=now+ timedelta(seconds=1))
        p2 = Post(body='Post from suzan', author=u2,timestamp=now+ timedelta(seconds=1))
        p3 = Post(body='Post from edo', author=u3,timestamp=now+ timedelta(seconds=1))
        p4 = Post(body='Post from togo', author=u4,timestamp=now+ timedelta(seconds=1))
        db.session.add_all([p1,p2,p3,p4])
        db.session.commit()

        #setup the followers
        u1.follow(u2) #john follows suzan
        u1.follow(u4) #john follows togo
        u2.follow(u3) #suzan follows edo
        u3.follow(u4) #john follows togo
        db.session.commit()

        #check the followed posts of each user
        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        self.assertEqual(f1,[p1,p2,p4])
        self.assertEqual(f2,[p2,p3])
        self.assertEqual(f3,[p3,p4])
        self.assertEqual(f4,[p4])


if __name__ == '__main__':
    unittest.main(verbosity=2)