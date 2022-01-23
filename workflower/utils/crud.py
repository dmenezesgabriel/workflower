import logging

logger = logging.getLogger("workflower.utils.crud")


def get_all(session, model, **kwargs):
    return session.query(model).filter_by(**kwargs).all()


def get_one(session, model, **kwargs):
    logger.debug(f"Getting one {model} , {dict(**kwargs)}")
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        logger.debug(f"Model {model} , {dict(**kwargs)} found")
        return instance
    else:
        logger.debug(f"Model {model} , {dict(**kwargs)} not found ")
    return None


def create(session, model, **kwargs):
    logger.debug(f"Creating {model} , {dict(**kwargs)}")
    instance = model(**kwargs)
    try:
        session.add(instance)
        session.commit()
        session.refresh(instance)
        logger.debug(f"Model {model} , {dict(**kwargs)} saved on database")
        return instance
    except Exception as error:
        logger.error(
            f"Writing model{model} , {dict(**kwargs)} failed. Error: {error}"
        )
        session.rollback()
        return None


def delete(session, model, **kwargs):
    logger.debug(f"Deleting {model} , {dict(**kwargs)}")
    instance = get_one(session, model, **kwargs)
    if instance:
        session.delete(instance)
        session.commit()


def update(session, model, filter_dict, new_attributes_dict):
    try:
        session.query(model).filter_by(**filter_dict).update(
            new_attributes_dict
        )
        session.commit()
        logger.debug(f"Model {model} , {dict(**filter_dict)} updated")
    except Exception as error:
        logger.error(
            f"Updating model{model} , {dict(**filter_dict)} "
            f"failed. Error: {error}"
        )
        session.rollback()


def get_or_create(session, model, **kwargs):
    instance = get_one(session, model, **kwargs)
    if instance:
        logger.debug("model already exists")
        return instance
    else:
        logger.debug("Creating model")
        return create(session, model, **kwargs)
