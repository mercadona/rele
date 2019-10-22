Filtering Messages
==================

Filter can be used to execute a subscription with specific parameters.
There's two types of filters, global or passing a filter_by parameter in the
subscription.


`filter_by` parameter
_____________________

This filter is a function that is supposed to return a boolean and this function
is passed as parameter `filter_by` in the subscription.

.. code:: python

    def landscape_filter(kwargs):
        return kwargs.get('type') == 'landscape'


    # This subscription is going to be called if in the `kwargs`
    # has a key type with value landscape

    @sub(topic='photo-updated', filter_by=landscape_filter)
    def sub_process_landscape_photos(data, **kwargs):
        print(f'Received a photo of type {kwargs.get("type")}')



Global Filter
_____________

This filter is specified in the settings with the key `FILTER_SUBS_BY`
that has a function as value.
In case a subscription has a filter already it's going to use it's own filter.

.. code:: python

    import os

    def landscape_filter(kwargs):
        return kwargs.get('type') == 'landscape'

    settings = {
        ...
        'FILTER_SUBS_BY': landscape_filter,
    }




