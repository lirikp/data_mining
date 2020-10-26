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
            session.flush()
            self.post['autor_db_id'] = entryWriter.id
        else:
            self.post['autor_db_id'] = id

        # Заливаем пост
        entryPost = models.Post(url=self.post['url'], img_url=self.post['img'], datetime_post=self.post['date'], writer_id=self.post['autor_db_id'])
        session.add(entryPost)
        session.flush()
        self.post['post_db_id'] = entryPost.id

        #Проверяем теги, получаем иды.
        for i, tag in enumerate(self.post['list_of_tags']):
            id = self.check_isset_tag(session, tag['name'])
            if not id:
                entryTag = models.Tag(name=tag['name'], url=tag['url'])
                session.add(entryTag)
                self.post['list_of_tags'][i]['db_id'] = self.check_isset_tag(session, tag['name'])

                # Заливаем таг посты
                entryPost.tag.append(entryTag)
                entryTag.posts.append(entryPost)
            else:
                self.post['list_of_tags'][i]['db_id'] = id

            session.flush()


        #Проверяем на наличие в базе комментаторов, подрисовываем id
        for i, comment in self.post['comments'].items():
            id = self.check_isset_writer(session, comment['writer'])
            if not id:
                entryWriter = models.Writer(name=comment['writer'], url=comment['url'])
                session.add(entryWriter)
                session.flush()
                self.post['comments'][i]['writer_db_id'] = self.check_isset_writer(session, comment['writer'])
            else:
                self.post['comments'][i]['writer_db_id'] = id
            print(i)

            #Заливаем комменты
            session.add(models.Comment(datetime_comment=comment['date'], body_comment=comment['text'], writer_id=id))
            session.flush()

        session.commit()
        session.close()
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

if __name__ == '__main__':
    c = dbConnector()
    print(c.SessionMaker)
