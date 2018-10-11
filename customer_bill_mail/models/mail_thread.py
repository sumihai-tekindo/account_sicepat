from openerp import SUPERUSER_ID
from openerp.osv import osv


class mail_thread(osv.AbstractModel):
	""" Update of mail_mail class, to add the signin URL to notifications. """
	_inherit = 'mail.thread'

	def message_get_reply_to(self, cr, uid, ids, default=None, context=None):
		res = super(mail_thread,self).message_get_reply_to(cr, uid, ids, default=None, context=context)
		# print "=======get_reply_to=========",context
		# print "=======get_reply_to2=========",res
		if context.get('override_reply_to',False):
			res.update({context.get('active_ids')[0]:context.get('override_reply_to')})
		return res