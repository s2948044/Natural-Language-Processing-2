import torch
import torch.nn as nn
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence


class LSTMLM(nn.Module):

    def __init__(self, vocabulary_size, dropout,
                 lstm_num_hidden=256, lstm_num_layers=2, device='cuda:0'):

        super(LSTMLM, self).__init__()

        # embedding
        self.embedding = nn.Embedding(num_embeddings=vocabulary_size,
                                      embedding_dim=lstm_num_hidden,
                                      padding_idx=1)

        # layers
        self.model = nn.LSTM(input_size=lstm_num_hidden,
                             hidden_size=lstm_num_hidden,
                             num_layers=lstm_num_layers,
                             bias=True,
                             dropout=dropout,
                             batch_first=True)
        self.linear = nn.Linear(lstm_num_hidden, vocabulary_size)

        self.to(device)

    def forward(self, x, h, c):
        embed = self.embedding(x)
        model, (h_n, c_n) = self.model(embed, (h, c))
        out = self.linear(model)
        print('out size', out.size())
        return out, h_n, c_n


class VAE(nn.Module):
    def __init__(
            self,
            vocabulary_size,
            dropout,
            lstm_num_hidden=128,
            lstm_num_layers=1,
            lstm_num_direction=2,
            num_latent=32,
            device='cuda:0'):

        super(VAE, self).__init__()

        self.lstm_num_hidden = lstm_num_hidden

        # encoder
        self.biLSTM_encoder = nn.LSTM(input_size=lstm_num_hidden,
                                      hidden_size=lstm_num_hidden,
                                      num_layers=lstm_num_layers,
                                      bias=True,
                                      dropout=dropout,
                                      batch_first=True,
                                      bidirectional=True)
        # embedding
        self.embedding = nn.Embedding(num_embeddings=vocabulary_size,
                                      embedding_dim=lstm_num_hidden,
                                      padding_idx=1)

        # latent size of z
        self.num_latent = num_latent

        # mean
        self.mu = nn.Linear(
            lstm_num_hidden *
            lstm_num_direction *
            lstm_num_layers,
            num_latent)  # *2 as it's bidirectional

        # for variance
        # *2 as it's bidirectional
        self.logvar = nn.Linear(
            lstm_num_hidden * lstm_num_direction * lstm_num_layers, num_latent)

        # to do, add this in according to proj description
        self.softplus = nn.Softplus()

        # latent to decoder
        # single layer single direction LSTM
        self.latent2decoder = nn.Linear(num_latent, lstm_num_hidden)

        # decoder
        self.LSTM_decoder = nn.LSTM(input_size=lstm_num_hidden,
                                    hidden_size=lstm_num_hidden,
                                    num_layers=lstm_num_layers,
                                    bias=True,
                                    dropout=dropout,
                                    batch_first=True,
                                    bidirectional=False)  # unidirectional

        self.LSTM_output = nn.Linear(lstm_num_hidden, vocabulary_size)

        self.device = device
        self.to(device)

    def forward(
            self,
            x,
            h_0,
            c_0,
            lengths_in_batch,
            importance_sampling_size=1):
        '''
        debugging log: just in case something goes wrong in the future, here's a list of things already checked
        # print('input(batch) size', x.size())
        # = batch * sent_len

        # h_N, (h_t, c_t) = self.biLSTM_encoder(embedded, (h_0, c_0))

        # print('h_N', h_N.size()) equals all h-outputs of each timestamp
        # = batch * sent_len * (lstm_num_hidden * #direction * #layer)
        # = batch * sent_len * (128*2)

        # print('h_t', h_t.size()) only the output of last timestamp t
        # = (#direction * #layer) * batch * lstm_num_hidden


        # checking that the last of h_N matches h_t
        # print('h_N 0th batch, last h, head', h_N[0, -1, 0:5])
        # print('h_t 0th batch, last h, head', h_t[:, 0, 0:5])

        # print('h_N', h_N.size())
        # print('h_N last ', torch.squeeze(h_N[:, -1, :]).size())

        # trying to pick the final feature h_t as the output of the biLSTM_encoder encoder
        # encoded = torch.squeeze(h_N[:, -1, :])


        # checking if pack_padded works
        # print('x', x)
        # print('lengths_in_batch',lengths_in_batch)
        # print('pack_padded_sequence(embedded)',pack_padded_sequence(embedded, lengths=lengths_in_batch,batch_first=True, enforce_sorted=False))


        # checking how to convert packed output from lstm to what we needed
        # print('x.size()',x.size())
        # print('lengths_in_batch',lengths_in_batch)
        # print('h_N_packed.data.shape ', h_N_packed.data.shape)

        # checking unpacked output
        # print('h_N_unpacked size', h_N_unpacked.size())
        # print('h_t_packed size', h_t_packed.size())
        # print('h_t_packed -1 ', h_t_packed[-1].size())

        # checking if encoder output works
        # encoder_output = torch.cat((h_t_packed[0], h_t_packed[1]),dim=1)
        # print('encoder_outputsize', encoder_output.size())
        # print('encoder_output', encoder_output)

        # checking dimensions of z
        # print('z rand', z)
        # print('z rand size', z.size())
        # print('mu shape', mu.shape)

        # checking decode
        # print('z.size()',z.size())
        # print('z',z)

        # decoder_input = self.latent2decoder(z)
        # print('decoder_input.size()',decoder_input.size())
        # print('decoder_input',decoder_input)

        # checking the final output matches the desired output dim
        print('decoder_output size and batch max length, lens_in_batch',decoder_output.size(), x.size(1), lengths_in_batch)
        print('x',x)
        '''

        # embed input
        embedded = self.embedding(x)

        # remove the paddings for faster computation
        packed_embedded = pack_padded_sequence(
            embedded,
            lengths=lengths_in_batch,
            batch_first=True,
            enforce_sorted=False)

        # feed pad_removed input into encoder
        # h_N_packed, (h_t_packed, c_t_packed) = self.biLSTM_encoder(packed_embedded, (h_0, c_0))
        _, (h_t_packed, _) = self.biLSTM_encoder(packed_embedded, (h_0, c_0))

        '''
        In case this is needed in future: to convert h_N_unpacked(padding removed) back to h_N_unpacked(with padding - padded position has [0,...0] as h_i); 
        dim of h_N_unpacked = batch * sent * (lstm_num_hidden * #direction * #layer)

        h_N_unpacked, lengths_in_batch_just_the_same = pad_packed_sequence(h_N_packed, batch_first=True)
        '''

        # The h_t_packed has weird dim = (num_layer * num direction) * batch * lstm_hidden = 2 * batch * 128(lstm_num_hidden)
        # have to concat the 2 directions of 128 hidden states back to 256
        # s.t. its dim now =  batch * 256
        encoder_output = torch.cat((h_t_packed[0], h_t_packed[1]), dim=1)

        # mean
        mu = self.mu(encoder_output)

        # log variance
        logvar = self.logvar(encoder_output)

        # std
        std = torch.exp(.5 * logvar)

        for k in range(importance_sampling_size):

            # introduce the epsilon randomness (actually default of requires
            # grad is already false, anyway ...)
            z = torch.randn((mu.shape), requires_grad=False).to(self.device)

            # compute z
            z = z * std + mu

            # compute the KL loss
            if k == 0:
                KL_loss = 0.5 * \
                    torch.sum(logvar.exp() + mu.pow(2) -
                              1 - logvar)  # initialize
            else:
                # add if there k>=1 samples of z
                KL_loss += 0.5 * \
                    torch.sum(logvar.exp() + mu.pow(2) - 1 - logvar)

            # map the latent dimensions of z back to the lstm_num_hidden
            # dimensions
            decoder_input = self.latent2decoder(z)

            # unsqueeze is for adding one dim of 1 to fit the input constraint of LSTM:
            # Inputs: input, (h_0, c_0); h_0 of shape (num_layers *
            # num_directions, batch, hidden_size)
            decoder_hidden_init = decoder_input.unsqueeze(0)

            # use this if want to init cell state with z as well:
            # decoder_cell_init = decoder_input.clone().unsqueeze(0)

            # Use this instead if take init cell state as empty: (which is the
            # first attempt)
            decoder_cell_init = torch.zeros(
                1, x.size(0), self.lstm_num_hidden).to(self.device)

            # feed this new z to the LSTM decoder to get all the hidden states
            # Am I right to feeed z to initial hidden states (instead of cell
            # states?)
            h_N_packed, (_, _) = self.LSTM_decoder(
                packed_embedded, (decoder_hidden_init, decoder_cell_init))

            # h_N_unpacked contains hidden states output of all timesteps
            # unused return value is the the lengths_in_batch: h_N_unpacked,
            # lengths_in_batch = pad_packed_sequence(h_N_packed,
            # batch_first=True)
            h_N_unpacked, _ = pad_packed_sequence(h_N_packed, batch_first=True)

            # decoder output is the fully-connected layer from num_hidden to vocab size,
            # Then in train.py we will use nn.CrossEntropy as the softmax to calculate the loss from this decoder_ouput
            # initialize st it now becomes (1, batch, sent_len, vocabsize)
            if k == 0:
                decoder_output = torch.unsqueeze(
                    self.LSTM_output(h_N_unpacked), dim=0)
            # use concat with unsqueeze. Finally it will become (k, batch,
            # sent_len, vocabsize)
            else:
                decoder_output = torch.cat((decoder_output, torch.unsqueeze(
                    self.LSTM_output(h_N_unpacked), dim=0)), dim=0)

        # print('decoder_output size', decoder_output.size())
        # print('KL_loss', KL_loss)

        return decoder_output, KL_loss

    @torch.no_grad()
    def sample(self, sample_size, vocab):

        z = torch.randn((sample_size, self.num_latent),
                        requires_grad=False).to(self.device)
        # print('z size', z.size())

        decoder_input = self.latent2decoder(z)

        # unsqueeze is for adding one dim of 1 to fit the input constraint of LSTM:
        # Inputs: input, (h_0, c_0); h_0 of shape (num_layers * num_directions,
        # batch, hidden_size)
        decoder_hidden_init = decoder_input.unsqueeze(0)

        # Use this instead if take init cell state as empty: (which is the
        # first attempt)
        decoder_cell_init = torch.zeros(
            1, sample_size, self.lstm_num_hidden).to(self.device)

        # create the sos inputs for size = (k, 1) then embed it to (k, 1,
        # lstm_num_hidden)
        sos_input = torch.LongTensor(
            [[4] for x in range(sample_size)]).to(self.device)
        embedded_sos_input = self.embedding(sos_input)
        '''
        for s in range(5): #mx sequence length

            # feed the first input to LSTM to get the next words
            # hidden_output of shape ( batch,seq_len=1, lstm_num_hidden)
            if s==0:
                hidden_output, (h,c) = self.LSTM_decoder(embedded_sos_input, (decoder_hidden_init, decoder_cell_init))
            else:
                hidden_output, (h,c) = self.LSTM_decoder(next_input, (h, c))

            decoder_output=self.LSTM_output(hidden_output)

            prediction = nn.functional.softmax(decoder_output, dim=2)#size = (s, 1, vocab_size)
            print('prediction', prediction)

            next_word = torch.argmax(prediction, dim=2) #k*1
            print('next_word',next_word)

            if s==0:
                prediction_greedy_max = next_word
            else:
                prediction_greedy_max = torch.cat((prediction_greedy_max, next_word),dim=1)

            next_input = self.embedding(next_word)
            print(next_word)
        '''
        for s in range(50):  # mx sequence length

            # feed the first input to LSTM to get the next words
            # hidden_output of shape ( batch,seq_len=1, lstm_num_hidden)
            if s == 0:
                hidden_output, (h, c) = self.LSTM_decoder(
                    embedded_sos_input, (decoder_hidden_init, decoder_cell_init))
            else:
                hidden_output, (h, c) = self.LSTM_decoder(
                    next_input, (decoder_hidden_init, decoder_cell_init))

            # get only the last hidden state
            decoder_output = self.LSTM_output(hidden_output[:, -1:, :])

            prediction = nn.functional.softmax(
                decoder_output, dim=2)  # size = (k, 1,vocab_size)
            # print('prediction', prediction)

            next_word = torch.argmax(prediction, dim=2)  # k*1
            # print('next_word',next_word)

            if s == 0:
                prediction_greedy_max = next_word
            else:
                prediction_greedy_max = torch.cat(
                    (prediction_greedy_max, next_word), dim=1)

            next_input = self.embedding(prediction_greedy_max)

        # print('prediction_greedy_max ', prediction_greedy_max)

        sampled_setences = [[vocab.i2w[word_idx]
                             for word_idx in k] for k in prediction_greedy_max]

        # print('sampled_setences',sampled_setences)

        return sampled_setences

    @torch.no_grad()
    def interpolation(self, vocab):
        # first make two z
        z1z2 = torch.randn((2, self.num_latent),
                           requires_grad=False).to(self.device)
        # print('z1z2 size', z1z2.size())

        # then we concat the mean
        mean_z = torch.unsqueeze(torch.mean(z1z2, dim=0), dim=0)
        z = torch.cat((z1z2, mean_z), dim=0)

        # then we concat z1*.8+ z2*.2 and likewise
        z_82 = torch.unsqueeze((z1z2[0] * .8 + z1z2[1] * .2), dim=0)
        z = torch.cat((z, z_82), dim=0)

        z_28 = torch.unsqueeze((z1z2[0] * .2 + z1z2[1] * .8), dim=0)
        z = torch.cat((z, z_28), dim=0)

        decoder_input = self.latent2decoder(z)

        # unsqueeze is for adding one dim of 1 to fit the input constraint of LSTM:
        # Inputs: input, (h_0, c_0); h_0 of shape (num_layers * num_directions,
        # batch, hidden_size)
        decoder_hidden_init = decoder_input.unsqueeze(0)

        # Use this instead if take init cell state as empty: (which is the
        # first attempt)
        decoder_cell_init = torch.zeros(
            1, 5, self.lstm_num_hidden).to(self.device)

        # create the sos inputs for size = (k, 1) then embed it to (k, 1,
        # lstm_num_hidden)
        sos_input = torch.LongTensor([[4] for x in range(5)]).to(self.device)
        embedded_sos_input = self.embedding(sos_input)

        for s in range(50):  # mx sequence length

            # feed the first input to LSTM to get the next words
            # hidden_output of shape ( batch,seq_len=1, lstm_num_hidden)
            if s == 0:
                hidden_output, (h, c) = self.LSTM_decoder(
                    embedded_sos_input, (decoder_hidden_init, decoder_cell_init))
            else:
                hidden_output, (h, c) = self.LSTM_decoder(
                    next_input, (decoder_hidden_init, decoder_cell_init))

            # get only the last hidden state
            decoder_output = self.LSTM_output(hidden_output[:, -1:, :])

            prediction = nn.functional.softmax(
                decoder_output, dim=2)  # size = (k, 1,vocab_size)
            # print('prediction', prediction)

            next_word = torch.argmax(prediction, dim=2)  # k*1
            # print('next_word',next_word)

            if s == 0:
                prediction_greedy_max = next_word
            else:
                prediction_greedy_max = torch.cat(
                    (prediction_greedy_max, next_word), dim=1)

            next_input = self.embedding(prediction_greedy_max)

        # print('prediction_greedy_max ', prediction_greedy_max)

        sampled_setences = [[vocab.i2w[word_idx]
                             for word_idx in k] for k in prediction_greedy_max]

        # print('sampled_setences',sampled_setences)

        return sampled_setences

    @torch.no_grad()
    def test_reconstruction(self, test_sent, vocab):
        x = test_sent
        lengths_in_batch = [1]
        importance_sampling_size = 10

        embedded = self.embedding(x)

        # remove the paddings for faster computation
        packed_embedded = pack_padded_sequence(
            embedded,
            lengths=lengths_in_batch,
            batch_first=True,
            enforce_sorted=False)

        # feed pad_removed input into encoder
        # h_N_packed, (h_t_packed, c_t_packed) = self.biLSTM_encoder(packed_embedded, (h_0, c_0))
        _, (h_t_packed, _) = self.biLSTM_encoder(packed_embedded)

        '''
        In case this is needed in future: to convert h_N_unpacked(padding removed) back to h_N_unpacked(with padding - padded position has [0,...0] as h_i); dim of h_N_unpacked = batch * sent * (lstm_num_hidden * #direction * #layer)

        h_N_unpacked, lengths_in_batch_just_the_same = pad_packed_sequence(h_N_packed, batch_first=True)
        '''

        # The h_t_packed has weird dim = (num_layer * num direction) * batch * lstm_hidden = 2 * batch * 128(lstm_num_hidden)
        # have to concat the 2 directions of 128 hidden states back to 256
        # s.t. its dim now =  batch * 256
        encoder_output = torch.cat((h_t_packed[0], h_t_packed[1]), dim=1)

        # mean
        mu = self.mu(encoder_output)

        # log variance
        logvar = self.logvar(encoder_output)

        # std
        std = torch.exp(.5 * logvar)

        for k in range(importance_sampling_size):

            # introduce the epsilon randomness (actually default of requires
            # grad is already false, anyway ...)
            init_z = torch.randn(
                (mu.shape), requires_grad=False).to(self.device)

            # compute z
            if k == 0:
                z = init_z * std + mu
            else:
                z = torch.cat((z, init_z * std + mu), dim=0)

        decoder_input = self.latent2decoder(z)

        # unsqueeze is for adding one dim of 1 to fit the input constraint of LSTM:
        # Inputs: input, (h_0, c_0); h_0 of shape (num_layers * num_directions,
        # batch, hidden_size)
        decoder_hidden_init = decoder_input.unsqueeze(0)

        # Use this instead if take init cell state as empty: (which is the
        # first attempt)
        decoder_cell_init = torch.zeros(
            1, 10, self.lstm_num_hidden).to(self.device)

        # create the sos inputs for size = (k, 1) then embed it to (k, 1,
        # lstm_num_hidden)
        sos_input = torch.LongTensor([[4] for x in range(10)]).to(self.device)
        embedded_sos_input = self.embedding(sos_input)

        for s in range(50):  # mx sequence length

            # feed the first input to LSTM to get the next words
            # hidden_output of shape ( batch,seq_len=1, lstm_num_hidden)
            if s == 0:
                hidden_output, (h, c) = self.LSTM_decoder(
                    embedded_sos_input, (decoder_hidden_init, decoder_cell_init))
            else:
                hidden_output, (h, c) = self.LSTM_decoder(
                    next_input, (decoder_hidden_init, decoder_cell_init))

            # get only the last hidden state
            decoder_output = self.LSTM_output(hidden_output[:, -1:, :])

            prediction = nn.functional.softmax(
                decoder_output, dim=2)  # size = (k, 1,vocab_size)
            # print('prediction', prediction)

            next_word = torch.argmax(prediction, dim=2)  # k*1
            # print('next_word',next_word)

            if s == 0:
                prediction_greedy_max = next_word
            else:
                prediction_greedy_max = torch.cat(
                    (prediction_greedy_max, next_word), dim=1)

            next_input = self.embedding(prediction_greedy_max)

        # print('prediction_greedy_max ', prediction_greedy_max)

        sampled_setences = [[vocab.i2w[word_idx]
                             for word_idx in k] for k in prediction_greedy_max]

        # print('sampled_setences',sampled_setences)

        return sampled_setences
