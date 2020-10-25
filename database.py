import models

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker



class dbConnector():

    post = {}

    def __init__(self):
        engine = create_engine('sqlite:///gb_blog.db')
        models.Base.metadata.create_all(bind=engine)
        self.SessionMaker = sessionmaker(bind=engine)

    def load_to_db(self, post):
        session = self.SessionMaker()
        self.post = post
        # Проверяем автора
        id = self.check_isset_writer(session, self.post['autor'])
        if not id:
            entryWriter = models.Writer(name=self.post['autor'], url=self.post['url'])
            session.add(entryWriter)
            session.commit()
            self.post['autor_db_id'] = entryWriter.id
        else:
            self.post['autor_db_id'] = id

        # Заливаем пост
        new_post = models.Post(url=self.post['url'], img_url=self.post['img'], datetime_post=self.post['date'], writer_id=self.post['autor_db_id'])
        session.add(new_post)
        session.commit()
        self.post['post_db_id'] = new_post.id

        #Проверяем теги, получаем иды.
        for i, tag in enumerate(self.post['list_of_tags']):
            id = self.check_isset_tag(session, tag['name'])
            if not id:
                entryTag = models.Tag(name=tag['name'], url=tag['url'])
                session.add(entryTag)
                session.commit()
                self.post['list_of_tags'][i]['db_id'] = self.check_isset_tag(session, tag['name'])
            else:
                self.post['list_of_tags'][i]['db_id'] = id

            #Заливаем таг посты
            new_tag_post = models.tag_post(post_id=self.post['post_db_id'], tag_id=id)
            session.add(new_tag_post)
            session.commit()


        #Проверяем на наличие в базе комментаторов, подрисовываем id
        for i, comment in self.post['comments'].items():
            id = self.check_isset_writer(session, comment['writer'])
            if not id:
                entryWriter = models.Writer(name=comment['writer'], url=comment['url'])
                session.add(entryWriter)
                session.commit()
                self.post['comments'][i]['writer_db_id'] = self.check_isset_writer(session, comment['writer'])
            else:
                self.post['comments'][i]['writer_db_id'] = id
            print(i)

            #Заливаем комменты
            session.add(models.Comment(datetime_comment=comment['date'], body_comment=comment['text'], writer_id=id))

        session.commit()





        session.flush()
        session.commit()
        # load comments

        print(post)

    def check_isset_writer(self, session, writer):
        if session.query(models.Writer).filter(models.Writer.name==writer).scalar():
            return session.query(models.Writer).filter(models.Writer.name==writer).one().id
        else:
            return False

    def check_isset_tag(self, session, tag):
        if session.query(models.Tag).filter(models.Tag.name == tag).scalar():
            return session.query(models.Tag).filter(models.Tag.name == tag).one().id
        else:
            return False


    def close(self):
        self.SessionMaker.close_all()


if __name__ == '__main__':
    c = dbConnector()
    print(c.SessionMaker)
