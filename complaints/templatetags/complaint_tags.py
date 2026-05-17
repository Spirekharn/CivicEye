from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def display_reporter(context, complaint):
    # Non-anonymous → show real name. Anonymous → show alias.
    # Super admin also sees the real name in brackets for oversight.
    viewer = context.get('request') and context['request'].user
    if not complaint.is_anonymous:
        return complaint.citizen.get_full_name() or complaint.citizen.username

    alias = complaint.anonymous_alias or 'Anonymous'
    if viewer and getattr(viewer, 'role', None) == 'super_admin':
        real = complaint.citizen.get_full_name() or complaint.citizen.username
        return f'{alias} (real: {real})'
    return alias


@register.simple_tag(takes_context=True)
def reporter_note(context, complaint):
    # Lets a citizen know when they're looking at their own anonymous report
    viewer = context.get('request') and context['request'].user
    if viewer and complaint.is_anonymous and complaint.citizen_id == viewer.id:
        return '(This is your anonymous report)'
    return ''
