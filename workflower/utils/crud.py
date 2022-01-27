import logging

logger = logging.getLogger("workflower.utils.crud")


def create(session, model_object, **kwargs):
    logger.debug(f"Creating {model_object} , {dict(**kwargs)}")
    instance = model_object(**kwargs)
    try:
        session.add(instance)
        session.commit()
        session.refresh(instance)
        logger.debug(
            f"Model {model_object} , {dict(**kwargs)} saved on database"
        )
        return instance
    except Exception as error:
        logger.error(
            f"Writing model_object{model_object} , {dict(**kwargs)} failed. Error: {error}"
        )
        session.rollback()
        return None


def delete(session, model_object, **kwargs):
    logger.debug(f"Deleting {model_object} , {dict(**kwargs)}")
    instance = get_one(session, model_object, **kwargs)
    if instance:
        session.delete(instance)
        session.commit()


def get_all(session, model_object, **kwargs):
    return session.query(model_object).filter_by(**kwargs).all()


def get_one(session, model_object, **kwargs):
    logger.debug(f"Getting one {model_object} , {dict(**kwargs)}")
    instance = session.query(model_object).filter_by(**kwargs).first()
    if instance:
        logger.debug(f"Model {model_object} , {dict(**kwargs)} found")
        return instance
    else:
        logger.debug(f"Model {model_object} , {dict(**kwargs)} not found ")
    return None


def update(session, model_object, filter_dict, new_attributes_dict):
    try:
        session.query(model_object).filter_by(**filter_dict).update(
            new_attributes_dict
        )
        session.commit()
        logger.debug(f"Model {model_object} , {dict(**filter_dict)} updated")
    except Exception as error:
        logger.error(
            f"Updating model_object{model_object} , {dict(**filter_dict)} "
            f"failed. Error: {error}"
        )
        session.rollback()


def get_or_create(session, model_object, **kwargs):
    """
    Get or create by name.
    """
    instance = get_one(session, model_object, name=kwargs["name"])
    if instance:
        logger.debug("model_object already exists")
        return instance
    else:
        logger.debug("Creating model_object")
        return create(session, model_object, **kwargs)
